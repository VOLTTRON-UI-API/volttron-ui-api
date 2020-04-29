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
