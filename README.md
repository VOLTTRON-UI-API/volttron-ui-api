# volttron-ui-api

## Installation

  - cd to volttron repository root
  - Clone repository into the volttron repository
  
    `git clone git@github.com:VOLTTRON-UI-API/volttron-ui-api.git VoltronUIAPI`
    
    or
    
    `git clone https://github.com/VOLTTRON-UI-API/volttron-ui-api.git VolttronUIAPI`
 
 - Activate volttron environment
  
    `. env/bin/activate`
    
  - Start volttron
  
    `./start-volttron` (or another method)
    
  - Run install-agent (`--start` and `--enable` optional)
  
    `python scripts/install-agent.py -s VolttronUIAPI -c VolttronUIAPI/config -t uiapi --start --enable`
    
  - Test agent (once running) at `/helloworld`
