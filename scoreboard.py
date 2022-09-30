
'''
Scoreboard functionality
Mainly used to make editing scoreboard information easier for the 'packet' info.
'''
class scoreboard:

    '''
    - 0-1: Shot clock 
    - 2-5: Game clock (and 19 for mode bit.) 
    - 6-8: Home score
    - 9-11: Away score
    - 12: Home foul
    - 13: Period information
    - 14: Away foul
    - 15: HomeTOL
    - 16: GuestTOL
    - 17: Possession Arrow (H for home and G for Guest)
    - 18: Horn. 'A' for on 'N' for off. 
    - 19: Determines to use a '.' or ':' for the game clock. 'C' for minutes, 'D' for seconds.
    - 20: Mode flag for different settings
    ---------------------------------------- <--- Other packet information
    - 21: Character to blink on in name
    - 22-34: Home team name
    - 35-47: Away team name
    '''
    def __init__(self, teams=False, byte_array = 0x0):

        # Default values for when the scoreboard starts up
        if(byte_array == 0x0):
            self.teams = teams 
            self.shot_clock = '30' # 2 ASCII bytes
            self.game_clock = '2500' # 4 bytes
            self.home_score = '000' # 3 bytes
            self.guest_score = '000' # 3 bytes
            self.home_foul = '0' # 1 byte
            self.period = '1' # 1 byte
            self.guest_foul = '0' # 1 byte
            self.home_tol = '3' # 1 byte
            self.guest_tol = '3' # 1 byte
            self.possession_arrow = 'H' # 1 byte
            self.horn = 'N' # 1 byte
            self.score_mode = 'C' # 1 byte 
            self.mode_flag = 'R' # 1 byte

            # Preset mode additions
            self.blinking_data = "1"
            self.home_team = "HOME" 
            self.guest_team = "GUEST"
    
        # Byte array has been added
        else: 
            self.teams = teams 
            self.shot_clock = chr(byte_array[0]) + chr(byte_array[1])
            self.game_clock = chr(byte_array[2]) + chr(byte_array[3]) + chr(byte_array[4]) + chr(byte_array[5])
            self.home_score = chr(byte_array[6]) + chr(byte_array[7]) + chr(byte_array[8])
            self.guest_score = chr(byte_array[9]) + chr(byte_array[10]) + chr(byte_array[11])
            self.home_foul = chr(byte_array[12])
            self.period = chr(byte_array[13])
            self.guest_foul = chr(byte_array[14])
            self.home_tol = chr(byte_array[15])
            self.guest_tol = chr(byte_array[16])
            self.possession_arrow = chr(byte_array[17])
            self.horn = chr(byte_array[18])
            self.score_mode = chr(byte_array[19])
            self.mode_flag = chr(byte_array[20])
    
            if(len(byte_array) > 21):
                self.blinking_data = chr(byte_array[21])
                self.home_team = "".join([chr(x) for x in byte_array[22:35]])
                self.guest_team = "".join([chr(x) for x in byte_array[35:47]])
            else: 
                # Preset mode additions
                self.blinking_data = "0"
                self.home_team = "Home" 
                self.guest_team = "Away"

    # The string representation of the scoreboard information. Used for sending packets.
    def __str__(self):
        string = self.shot_clock.rjust(2, '0')
        string += self.game_clock.rjust(4, '0')
        string += self.home_score.rjust(3, '0')
        string += self.guest_score.rjust(3, '0')
        string += self.home_foul.rjust(1, '0')
        string += self.period.rjust(1, '0')
        string += self.guest_foul.rjust(1, '0')
        string += self.home_tol.rjust(1, '0')
        string += self.guest_tol.rjust(1, '0')
        string += self.possession_arrow
        string += self.horn 
        string += self.score_mode 
        string += self.mode_flag

        # Add the team names and blinking information as well
        if(self.teams == True):
            string += self.blinking_data
            string += self.home_team.ljust(13, '-')
            string += self.guest_team.ljust(13, '-')
        return string

    # Display scoreboard contents for debugging
    def print_scoreboard(self):
        print("Shot Clock: {}".format(self.shot_clock))

        if(self.score_mode == 'C'):
            div_character = ":"
        else: 
            div_character = '.'
        print("Game Clock: {}{}{}".format(self.game_clock[0:2], div_character, self.game_clock[2:4]))
        print("Home Score: {}".format(self.home_score))
        print("Guest Score: {}".format(self.guest_score))
        print("Home Foul: {}".format(self.home_foul))
        print("Game Period: {}".format(self.period))
        print("Guest Foul: {}".format(self.guest_foul))
        print("Home Timeouts Left: {}".format(self.home_tol))
        print("Guest Timeouts Left: {}".format(self.guest_tol))

        if(self.horn == 'A'):
            print("Horn Setting: {}".format("on"))
        elif(self.horn == 'N'):
            print("Horn Setting: {}".format("off"))

        if(self.possession_arrow == "H"):
            print("Posession Arrow: {}".format("Home Team"))
        elif(self.possession_arrow == "Guest"):
            print("Posession Arrow: {}".format("Guest Team"))


        if(self.teams):
            print("Home Team: {}".format(self.home_team))
            print("Guest Team: {}".format(self.guest_team))

    '''
    Decrease the time of the game
    '''
    def decrease_game_clock(self):
        clock = self.game_clock
        
        beginning = int(clock[0:2])
        end = int(clock[2:4])

        print(beginning, end) 
        # Game has ended
        if((beginning == 0 and end == 0)):
            return 0
        
        # Switching from minutes to seconds as MSB
        elif(beginning == 1 and end == 0 and self.score_mode == 'C'):
            print("Enter?")
            self.score_mode = 'D'
            beginning = 59
            end = 99
        
        # Minutes as MSB
        elif(self.score_mode == 'C'):
            if(end == 0):
                beginning = beginning - 1
                end = 59
            else: 
                end = end - 1

        # Seconds as MSB
        elif(self.score_mode == 'D'):
            if(end == 0):
                end = 99
                beginning = beginning - 1
            else: 
                end = end - 1
        

        # Pad the numbers properly
        beginning = str(beginning).rjust(2, '0')
        end = str(end).rjust(2, '0')
        self.game_clock = beginning + end
        return self.game_clock

    def decrease_shot_clock(self):

        # Clock has expired!
        if(int(self.shot_clock) == 0):
            return 0 

        shot_clock = int(self.shot_clock) - 1

        self.shot_clock = str(shot_clock).rjust(2, '0')
        return self.shot_clock
    
    # Turn ON the horn
    def horn_on(self):

        # Already on!
        if(self.horn == 'A'):
            return True 
        
        # Command to turn ON the horn
        self.horn = 'A'

        return True

    # Turn off the horn
    def horn_off(self):

        # Already off!
        if(self.horn == 'N'):
            return True 
        
        # Command to turn OFF the horn
        self.horn = 'N'

        return True

    '''
    Getters & Setters for operations on the scoreboard
    '''
    def get_game_clock(self):
        if(self.score_mode == 'C'):
            character = ":"
        else: 
            character = '.'
        
        beginning = self.game_clock[0:2]
        end = self.game_clock[2:4]

        return beginning + character + end

    def set_game_clock(self, front, back, minutes_msb=True):
        if(len(str(front)) > 2 or len(str(back)) > 2):
            return False
        
        # Minutes & seconds or seconds and milliseconds
        if(minutes_msb == False or front == "0" or front == "00"):
            self.score_mode = 'D' # seconds and milliseconds
            self.game_clock = str(back).rjust(2, '0') + "".rjust(2, '0')
        else: 
            self.score_mode = 'C' # Minutes & seconds
            self.game_clock = str(front).rjust(2, '0') + back.rjust(2, '0')
        return True

    def set_shot_clock(self, time):
        if(len(str(time)) > 2):
            return False 
        
        self.shot_clock = str(time)

    def get_shot_clock(self):
        return self.shot_clock.rjust(2, '0')

    def get_home_team(self):
        return self.home_team

    def set_home_team(self, name):
        if(self.teams == False):
            return False
        
        if(len(name) > 13):
            name = name[0:13]
        self.home_team = name.ljust(13, '-')

        return True 

    def get_guest_team(self):
        return self.guest_team

    def set_guest_team(self, name):
        if(self.teams == False):
            return False
        
        if(len(name) > 13):
            name = name[0:13]
        self.guest_team = name.ljust(13, '-')

        return True

    def get_home_foul(self):
        return self.home_foul
        
    def set_home_foul(self, num):
        self.home_foul = str(num)
        return True

    def get_guest_foul(self):
        return self.guest_foul

    def set_guest_foul(self, num):
        self.guest_foul = str(num)
        return True

    def get_period(self):
        return self.period 

    def set_period(self, num):
        if(num > 9 or num < 0):
            return False

        self.period = str(num)
        return True
    
    def get_home_tol(self):
        return self.home_tol 

    '''
    Numbers 0-4 then P are expected. However, it will render all other characters besides 5-9.
    NBA basketball scoreboard, for some reason.
    '''
    def set_home_tol(self, num):
        if(num > 9 or num < 0):
            return False

        self.home_tol = str(num)
        return True

    def get_guest_tol(self):
        return self.guest_tol

    def set_guest_tol(self, num):
        if(num > 9 or num < 0):
            return False

        self.guest_tol = str(num)
        return True    

    def get_blink(self):
        return self.blinking_data

    # Blinking operation when in the 'preset' mode.
    '''
    0-Q are the allowed operations. 
    If this is set to '1', then it will blink the first character on the scoreboard for the guest team. 
    If this is set to 'E', then it will blink the first charcter on the scoreboard for the home team. 
    '''
    def set_blink(self, num):
        self.blinking_data = str(num)

    def is_teams_on(self):
        return self.teams

    def set_teams(self, team_on=True):
        self.teams = team_on

        # Preset mode additions
        self.blinking_data = "0"
        self.home_team = "Home" 
        self.guest_team = "Guest"

    def set_home_score(self, score): 
        if(len(str(score)) > 3):
            return False
        score = str(score).replace(" ","")

        self.home_score = str(score).rjust(3, '0')

    def set_guest_score(self, score): 
        if(len(str(score)) > 3):
            return False
        
        score = str(score).replace(" ","")
        self.guest_score = str(score).rjust(3, '0')

    '''
    'G' makes pictureBox3 visible and pictureBox4 invisible. Guest Side.
    'H' makes pictureBox4 visible and pictureBox3 invisible. Home Side.
    '''
    def set_possession_arrow(self, value):
        self.possession_arrow = value

    def flip_possession_arrow(self): 
        if(self.possession_arrow == 'G'):
            self.possession_arrow = 'H'
        elif(self.possession_arrow == 'H'):
            self.possession_arrow = 'G'

    def get_score_mode(self): 
        return self.score_mode

if __name__ == "__main__":
    #data = [0x33,0x30,0x32,0x35,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x31,0x30,0x33,0x33,0x48,0x4e,0x43,0x47]

    board = scoreboard()
    print(board)
    for i in range(30):
        board.decrease_game_clock()
        print(board)

