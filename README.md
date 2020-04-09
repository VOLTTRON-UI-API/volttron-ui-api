# volttron-ui-api

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
