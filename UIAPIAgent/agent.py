"""
Agent documentation goes here.
"""

__docformat__ = 'reStructuredText'

import logging
import sys
from volttron.platform.agent import utils
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
        #Register Test Endpoint
        self.vip.web.register_endpoint(r'/helloworld', lambda env,data: "Hello World!")
        self.vip.web.register_endpoint(r'/devices', self.endpoint_list_devices)

        #Example publish to pubsub
        #self.vip.pubsub.publish('pubsub', "some/random/topic", message="HI!")

        #Exmaple RPC call
        #self.vip.rpc.call("some_agent", "some_method", arg1, arg2)

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

    @Core.receiver("onstop")
    def onstop(self, sender, **kwargs):
        """
        This method is called when the Agent is about to shutdown, but before it disconnects from
        the message bus.
        """
        pass

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
