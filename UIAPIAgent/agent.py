"""
Agent documentation goes here.
"""

__docformat__ = 'reStructuredText'

import logging
import requests
import sys
from token_handler import TokenHandler
from volttron.platform.agent import utils
from volttron.platform.agent.known_identities import *
from volttron.platform.vip.agent import Agent, Core, RPC

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


def UIAPIAgent(config_path, **kwargs):
    """Parses the Agent configuration and returns an instance of
    the agent created using that configuration.

    :param config_path: Path to a configuration file.

    :type config_path: str
    :returns: Uiapiagent
    :rtype: Uiapiagent
    """
    try:
        config = utils.load_config(config_path)
    except StandardError:
        config = {}

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    setting1 = int(config.get('setting1', 1))
    setting2 = config.get('setting2', "some/random/topic")

    return Uiapiagent(setting1,
                          setting2,
                          **kwargs)


# TODO: Refactor to match RPC.export implementation
_agent_routes = []
def agent_route(route_regex):
    '''Register decorated function at the given route.

    Requires complementary code in `onstart` method.
    Also Requires that function is exported RPC function. (i.e. decorated with @RPC.export)

    NOTE: Accepts regex expressions
    '''
    def register_agent_route(method):
        _agent_routes.append((route_regex, method.__name__))
        return method
    return register_agent_route

_agent_endpoints = []
def endpoint(endpoint_path):
    '''Register decorated function at the given endpoint.

    Requires complementary code in `onstart` method.

    NOTE: Use agent_route for regex matching.
    '''
    def register_endpoint(method):
        _agent_endpoints.append((endpoint_path, method.__name__))
        return method
    return register_endpoint

class Uiapiagent(Agent):
    """
    Document agent constructor here.
    """

    def __init__(self, setting1=1, setting2="some/random/topic",
                 **kwargs):
        super(Uiapiagent, self).__init__(enable_web=True, **kwargs)
        _log.debug("vip_identity: " + self.core.identity)

        self.setting1 = setting1
        self.setting2 = setting2

        self.default_config = {"setting1": setting1,
                               "setting2": setting2}

        self._auth = TokenHandler()

        #Set a default configuration to ensure that self.configure is called immediately to setup
        #the agent.
        self.vip.config.set_default("config", self.default_config)
        #Hook self.configure up to changes to the configuration file "config".
        self.vip.config.subscribe(self.configure, actions=["NEW", "UPDATE"], pattern="config")

    def configure(self, config_name, action, contents):
        """
        Called after the Agent has connected to the message bus. If a configuration exists at startup
        this will be called before onstart.

        Is called every time the configuration in the store changes.
        """
        config = self.default_config.copy()
        config.update(contents)

        _log.debug("Configuring Agent")

        try:
            setting1 = int(config["setting1"])
            setting2 = str(config["setting2"])
        except ValueError as e:
            _log.error("ERROR PROCESSING CONFIGURATION: {}".format(e))
            return

        self.setting1 = setting1
        self.setting2 = setting2

        self._create_subscriptions(self.setting2)

    def _create_subscriptions(self, topic):
        #Unsubscribe from everything.
        self.vip.pubsub.unsubscribe("pubsub", None, None)

        self.vip.pubsub.subscribe(peer='pubsub',
                                  prefix=topic,
                                  callback=self._handle_publish)

    def _handle_publish(self, peer, sender, bus, topic, headers,
                                message):
        pass

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        This is method is called once the Agent has successfully connected to the platform.
        This is a good place to setup subscriptions if they are not dynamic or
        do any other startup activities that require a connection to the message bus.
        Called after any configurations methods that are called at startup.

        Usually not needed if using the configuration store.
        """

        self.vip.web.register_endpoint(r'/helloworld', lambda env,data: "Hello World!") #Test Endpoint

        # NOTE: See _agent_route and _endpoint decorators for how the functions are collected.
        for route_regex, method_name in _agent_routes:
            self.vip.rpc.call(MASTER_WEB, 'register_agent_route', route_regex, method_name).get(timeout=10)
        for endpoint_path, method_name in _agent_endpoints:
            _log.debug((endpoint_path, method_name))
            self.vip.web.register_endpoint(endpoint_path, getattr(self, method_name))

        #Example publish to pubsub
        #self.vip.pubsub.publish('pubsub', "some/random/topic", message="HI!")

        #Exmaple RPC call
        #self.vip.rpc.call("some_agent", "some_method", arg1, arg2)

    @endpoint(r'/devices')
    def endpoint_list_devices(self, env, data):
        """List devices on all platforms with point and status info.

        Returns: JSON dict of devices nested by platform:
        ```
        {
        "volttron1": {
            "devices/fake-campus/fake-building/fake-device": {
                "points": [
                    "Heartbeat",
                    "temperature",
                    "PowerState",
                    "ValveState",
                    "EKG_Sin",
                    "EKG_Cos"
                ],
                "health": {
                    "status": "GOOD",
                    "context": "Last received data on: 2020-04-02T01:39:10.025580+00:00",
                    "last_updated": "2020-04-02T01:39:10.025729+00:00"
                },
                "last_publish_utc": "2020-04-02T01:39:10.025580+00:00"
            }
        }
        }
        ```
        """
        _log.debug('roanmh: Entered list_devices')

        # Call and format core function
        return self.list_devices()

    @agent_route(r'/devices/.*')
    @RPC.export
    def enpoint_device(self, env, data):
        device_name = env['PATH_INFO'].replace('/devices/', '', 1)
        return device_name

    @agent_route(r'/points/.*')
    @RPC.export
    def endpoint_point(self, env, data):
        """Show or set data of a given endpoint.

        Returns: JSON dict of point data.
        """
        if self.check_authorization(env, data):
            return "Test"
        return "Unauthorized"

    def list_devices(self):
        """List device information by platform."""
        response = {}
        for platform_connection_id in self.list_platform_connections():
            platform_name = platform_connection_id.split('.')[0]
            devices = self.vip.rpc.call(platform_connection_id, 'get_devices').get()
            response[platform_name] = devices

        return response

    def list_platform_connections(self):
        """List VCConnection agents which represent each platform."""
        platform_connection_agents = [x for x in self.vip.peerlist().get(timeout=5)
                     if x.startswith('vcp-') or x.endswith('.platform.agent')]
        return platform_connection_agents

    def _make_token(self, data, env):
        """Generate an API token if authorized"""
        if 'username' not in data or 'password' not in data:
            return "Username and password must be specified."

        # TODO Return early since auth is not yet working
        token = self._auth.generate_token(data['username'],
                                          data['password'])
        return { 'token' : token }
        # TODO Remove to here

        # Check if user information is correct
        auth_url = "{url_scheme}://{HTTP_HOST}/authenticate".format(
            url_scheme=env['wsgi.url_scheme'],
            HTTP_HOST=env['HTTP_HOST'])
        args = {'username': data['username'],
                'password': data['password'],
                'ip': env['REMOTE_ADDR']}
        resp = requests.post(auth_url, json=args, verify=False)

        if resp.ok and resp.text:
            token = self._auth.generate_token(data['username'],
                                              data['password'])
            return { 'token' : token }
        else:
            return "Invalid username/password specified."

    def _get_token(self, data, env):
        """Retrieve API token"""
        # if username or password are missing, specify correct format
        if 'username' not in data or 'password' not in data:
            return { 'username': '',
                     'password': '',
                     'token':    '' }

        token = self._auth.retrieve_token(data['username'],
                                          data['password'])
        if token:
            return { 'token': token }

        return "No token available for specified username/password."

    def _remove_token(self, data, env):
        """Remove API token for specified user"""
        if 'username' not in data or 'password' not in data:
            return "Username and password must be specified."

        return self._auth.remove_token(data['username'], data['password'])

    @endpoint(r'/auth')
    def handle_auth(self, env, data):
        """Handle requests to the auth endpoint"""
        methods = { 'POST':     self._make_token,
                    'GET':      self._get_token,
                    'DELETE':   self._remove_token }

        request_method = env['REQUEST_METHOD'].upper()
        if request_method in methods:
            return methods[request_method](data, env)

        return "Method not supported."

    def check_authorization(self, env, data):
        """Verify API token"""
        try:
            token = env['HTTP_AUTHORIZATION'].split()[1]
            return self._auth.validate_token(token)
        except (KeyError, IndexError):
            return False

    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        """
        This method is called when the Agent is about to shutdown, but before it disconnects from
        the message bus.
        """
        self.vip.web.unregister_all_routes()


    @RPC.export
    def rpc_method(self, arg1, arg2, kwarg1=None, kwarg2=None):
        """
        RPC method

        May be called from another agent via self.core.rpc.call """
        return self.setting1 + arg1 - arg2


def main():
    """Main method called to start the agent."""
    utils.vip_main(UIAPIAgent,
                   version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
