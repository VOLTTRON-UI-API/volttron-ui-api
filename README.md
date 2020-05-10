# VOLTTRON UI API

*A RESTful API design for a usable and broadly capable remote access to a VOLTTRON Deployment.*


## Purpose

The UI API will function as a distinct unit to expand on the capabilities of VOLTTRON Central and the JsonRPC API. VOLTTRON Central and the JsonRPC API provide for a configuration, setup, and limited monitoring from a remote connection via an HTTP interface. The community has expresed interest in further remote capabilties including: control of devices and points, set-point control through the actuator agent, arbitrary execution of RPC and pub-sub actions, and a consistent, usable interface for these varied functions.

Given this problem statement, the UI API proposes a REStful API that is implemented as a separate agent and only relies on the VOLLTRON Central Platform Agent.


## Design

### REST Architecture

The REST Architecture is a well known standard for creating usable and robust APIs. REST was chosen over JsonRPC for its fit with our purpose. JsonRPC would keep the API interface very similar to the existing functions exposed by the Agents, however we believe it would sacrifice usability in our case.

### Distinct Agent

The API is implemented in a single agent, which allows easy installation. The agent only requires the VOLTTRON Central Platform Agent and whatever agents are called for by the use-case. The agent does not rely on VOLLTRON Central.

## Interface

### Platform Tree

**A complete, hierarchal view of the deployment.**

Currently not-implemented for the proof-of-concept. However this is where the most 'restful' design is possible. Devices, Platforms, et al. will be represented as objects and collections and the endpoints will be discover-able through the links provided by the API.

*Note:* This section should be treated as a draft and a stub of the interface. Changes and expansions will be required.

---

#### `/platform/` | `GET`

Return a list of platforms and links to their object pages.

*NOTE:* This is the only currently implemented function in this section

*NOTE:* Links are currently returned as `Null`, not what is shown here.

**Request Body:** *Empty*

**Response Body:**
```json
{
    "<platform_name>": "/platform/<platform_name>"
}
```

---

#### `/platform/<platform_name>` | `GET`

Return information about the platform and links to related entities.

**Request Body:** *Empty*

**Response Body:**

```json
{
    "status": { <status> },
    "links": {
        "devices": "/platform/<platform_name>/device",
        "message_bus": "/platform/<platform_name>/bus",
        "agents": "/platform/<platform_name>/agent",
        "config": "/platform/<platform_name>/config"
    }
}
```

---

#### `/platform/<platform>/devices` | `GET`

Return a list of devices on the specified platform.

**Request Body:** *Empty*

**Response Body:**

```json
{
    "/devices/fake-campus/fake-building/fake-device": {
        "platform": "<platform_name>",
        "link": "/devices/<platform_name>/fake-campus/fake-building/fake-device"
    }
}
```

---

#### `/platform/<platform>/bus` | `GET`

Return the status of the message bus on the specified platform and provide links to related objects.

**Request Body:** *Empty*

**Response Body:**

```json
{
    "status": { <status> },
    "links": {
        "subscriptions": "/platform/<platform>/bus/sub",
        "publish": "/platform/<platform>/bus/pub"
    }
}
```

---

#### `/platform/<platform_name>/bus/sub` | `GET`

Return a list of subscriptions on the specified platform.

*NOTE:* The subscriptions are specifically those made and maintained by the the UI API Agent. **NOT** all the subscriptions active on the platform.

*NOTE:* Endpoints could be created under this to return a list of last values or bind objects, instead of the links. i.e. `/platform/<platform_name>/bus/sub/val`

**Request Body:** *Empty*

**Response Body:**

```json
{
    "<topic>": "/platform/<platform_name>/bus/sub/<topic>"
}
```

---

#### `/platform/<platform>/bus/sub/<topic>` | `GET`

Return the subscription of the topic or error. 

**Request Body:** *Empty*

**Response Body:**

- If subscription exists:
  ```json
  {
      "topic": "<topic>",
      "push_bind": <bind_object or Null>,
      "last_value": "<last_value>"
  }
  ```
or

- If subscription does not exist: `404 Subscription Not Found`

---

#### `/platform/<platform>/bus/sub/<topic>` | `POST`

Create or modify the specified subscription and confirm the details or return an error.

**Request Body:**

```json
{
    "push_bind": <bind_object or Null>
}
```

**Response Body:**

- If no errors"
  ```json
  {
      "topic": "<topic>",
      "push_bind": <bind_obaject or Null>,
      "last_value": "<last_value>"
  }
  ```
  
- If errors: `<error_code> <error_message>`

---

#### `/platform/<platform>/bus/pub` | `GET`

Return a list of past publishes with links.

**Request Body:** *Empty*

**Response Body:**
```json
{
    "<topic>": "/platform/<platform>/bus/pub/<topic>"
}
```

---

#### `/platform/<platform>/bus/pub/<topic>` | `POST`

Create a publish at the specified topic on the specified platform and confirm the details or return an error.

**Request Body:**

```json
{
    "value": "<value>"
}
```

**Response Body:**

- If no errors
  ```json
  {
      "topic": "<topic>",
      "value": "<value>",
  }
  ```
- If errors: `<error_code> <error_message>`

---

#### `/platform/<platform_name>/agent` | `GET`

Return a list of agents on the specified platform.

*NOTE:* To be expanded upon.

**Request Body:** *Empty*

**Response Body:**

```json
{
    "<vip_identity>: "/platform/<platform_name>/agent/<vip_identity>"
}
```

---

#### `/platform/<platform_name>/config` | `GET`

Return a list of configurations on the specified platform.

*NOTE:* To be expanded upon.

**Request Body:** *Empty*

**Response Body:**

```json
{
    "<config_name>: "/platform/<platform_name>/agent/<config_name>"
}
```

---

### Devices

**A shortcut to using devices in the tree and for getting and setting points**

---

#### `/devices` |  `GET`

Returns list of devices on all platforms.

**Request Body:** *Empty*

**Response Body:**
```json
{
    "/devices/fake-campus/fake-building/fake-device": {
        "platform": "volttron1",
        "link": "/devices/volttron1/fake-campus/fake-building/fake-device"
    }
}
```

---

#### `/devices/<device_path>/all` |  `GET`

Returns a list of points and their values across all platforms.

**Request Body:** *Empty*

**Response Body:**
```json
{
   "<point>": "<values>"
}
```

---

#### `/devices/<device_path>/pt` |  `GET`

Returns list of links to the points on the devices. 

*NOTE:* Endpoints could be created under this to return a list of last values or bind objects, instead of the links. i.e. `/devices/<device_path>/pt/val`

**Request Body:** *Empty*

**Response Body:**
```json
{
    "<topic>": "/devices/<device_path>/pt/<topic>"
}
```

---

#### `/devices/<device_path>/pt/<point>` |  `GET`

Returns the value and type of the specified point. 

*NOTE: Ideally would also return if the point is writable.* `"writable": <boolean>`

**Request Body:** *Empty*

**Response Body:**
```json
{
    "value": <value>,
    "type": "<type>"
}
```

---

#### `/devices/<device_path>/pt/<point>` |  `POST`

Sets value of the point and returns its new value and type. 

*NOTE: Ideally would also return if the point is writable.* `"writable": <boolean>`

**Request Body:** 
```json
{
    "value": <value>
}
```

**Response Body:**
```json
{
    "value": <value>,
    "type": "<type>"
}
```

---

#### `/devices/heirarchy` |  `GET`
Returns list of devices on all platforms with point and status info.

**Request Body:** *Empty*

**Response Body:**
```json
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
```

---

### Auth

A Valid token is required for all other endpoints. The Token is created here and used by including a header in the request with the name `Authorization` and value `BASIC <token>`.

---
#### `/auth` | `GET` 

Returns token attached to specified username and password.

- **Request Body:** *Empty*

  **Response Body:**
  
  ```json
  {
      "username": "",	
      "password": ""
  }
  ```

- **Request Body:**

  ```json
  {
      "username": "<username>",
      "password": "<password>"
  }
  ```
  
  **Response Body:**
  
  - With valid username and password:
	  ```json
	  {
		    "token": "<token>"
	  }
	  ```

  - With invalid username and password: `200 No token available for specified username/password.`

    *NOTE:* The response code should be changed to an error code, not 200.
  
---

#### `/auth` | `POST` 

Returns and attaches token to specified username and password.

**Request Body:**

```json
{
    "username": "username",
    "password": "<password>"
}
```

**Response Body:**
- With valid username and password:
  ```json
  {
      "token": "<token>"
  }
  ```

- With invalid username and password: `200 Invalid username/password specified.`

  *NOTE:* The response code should be changed to an error code, not 200.

## Installation

  - cd to volttron repository root
  - Clone repository into the volttron repository
  
    `git clone git@github.com:VOLTTRON-UI-API/volttron-ui-api.git`
    
    or
    
    `git clone https://github.com/VOLTTRON-UI-API/volttron-ui-api.git`
 
 - Activate volttron environment
  
    `. env/bin/activate`
    
  - Start volttron
  
    `./start-volttron` (or another method)
    
  - Run install-agent (`--start` and `--enable` optional)
  
    `python scripts/install-agent.py -s volttron-ui-api -c volttron-ui-api/config -t uiapi --start --enable`
    
  - Test agent (once running) at `https://<host>:8443/helloworld`
