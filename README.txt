- installation
    # pip3 install -r requirements.txt
- configuration
    In the config.py
    * copy the csv file to this directory
    * replace destination address to DEST_ADDRESS
    * replace csv file name to SOURCE_FILE_NAME
    * if you want test_net, change USING_TEST_NET to True
    * if you want to wait for confirmation every transaction, change IS_WAIT_FOR_CONFIRM to True
    * you can change gas level as ETH_GAS_LEVEL
    * SLEEP_TIME_PER_ADDRESS: wait time per addresses
- run
    # python3 main.py