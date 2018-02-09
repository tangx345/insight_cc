# -*- coding: utf-8 -*-
"""
Spyder Editor

copyright: Yang Tang 02/08/2018
"""
import sys
import math

class DonationAnalysis():
    
    def __init__(self):
        #### initialize variables
        ####    dict donors : records the earliest donation for each donor, key = 'ZIP_CODE' + 'NAME' = donor identity, value = [CMTE_ID, TRANSACTION_DT, TRANSACTION_AMT]
        ####    dict rcpts : records the transaction number and total amount for each recipient and calender year, key = 'YEAR' + 'CMTE_ID' = recipient identity, value = [TRANSACTION_TOT_AMT, TRANSACTION_NO]
        ####    list cur_in : records the useful information from current input stream of 'itcont.txt'
        ####    list cur_out : records the information needs to be output to 'repeat_donors.txt' if a repeat donor is found
        ####    float pct : the percentage read from 'percentile.txt', will be used to calculate percentile
        self.donors = {}
        self.rcpts = {}
        self.cur_in = []
        self.cur_out = []
        self.pct = 0.0
    
    def setPercentage(self, percentage_value):
        #### pass the percentage value read from 'percentile.txt' to self.pct
        self.pct = percentage_value
    
    def findInsertPos(self, num_hist, num):
        #### use binary search to find where a new TRANSACTION_AMT should be placed in recorded TRANSACTION_AMT list
        #### this will help maintain the TRANSACTION_AMT list in order for percentile calculation
        ####    input : list num_list which contains amount array and already in order, float num : new amount to be inserted
        ####    output : the index that num should be inserted
        l = 0
        r = len(num_hist) - 1
        if num_hist[l] >= num:
            return l
        if num_hist[r] < num:
            return r + 1
        while l + 1 < r:
            mid = (l + r) // 2
            if num_hist[mid] >= num:
                r = mid
            else:
                l = mid
        return r
    
    def output(self):
        #### pass the output information to outside class for recording
        return self.cur_out
    
    def checkInput(self, input_data):
        #### check if the information in input_data is outliner 
        ####     input : list of string which should contain [CMTE_ID, NAME, ZIP_CODE, TRANSACTION_DT, TRANSACTION_AMT, OTHER_ID]
        ####     output : False if input is invalid can be ignored; True if input is valid
        # check length for every member
        if len(input_data[0]) == 0 or len(input_data[1]) == 0 or len(input_data[2]) < 5 or len(input_data[3]) != 8 or len(input_data[4]) == 0 or len(input_data[5]) > 0:
            return False
        # check if NAME only contain letters, space, comma or period
        for c in input_data[1]:
            if not (c == ',' or c == ' ' or c == '.' or c.isalpha()):
                return False
        # check if ZIP_CODE only contain digits, and set it to only first 5 digits
        for x in input_data[2]:
            if not x.isdigit():
                return False
        input_data[2] = input_data[2][:5]
        # check if TRANSACTION_DT only contain digits, and follow date number constrains, then set it to yyyymmdd for later comparison
        for x in input_data[3]:
            if not x.isdigit():
                return False
        month = int(input_data[3][:2])
        day = int(input_data[3][2:4])
        year = int(input_data[3][4:])
        if month > 12 or month == 0 or day > 31 or day == 0 or year < 2000 or year > 2018:
            return False
        input_data[3] = input_data[3][4:] + input_data[3][:2] + input_data[3][2:4]
        # check if TRANSACTION_AMT is a float number
        try:
            float(input_data[4])
        except ValueError:
            return False
        # stream passes all check and recorded to cur_in, OTHER_ID is dropped
        self.cur_in = input_data[:-1].copy()
        return True
        
    def checkRepeatDonor(self):
        #### check if the donor whose information is in self.cur_in is a repeat donor
        ####    input : void
        ####    output : True if this donor is repeart donor, and pass the information needed to be written to output file to self.cur_out, False otherwise
        donor_key = self.cur_in[2] + self.cur_in[1]
        if donor_key in self.donors:
            # found a repeat donor
            cur_don = [self.cur_in[0], self.cur_in[3], self.cur_in[4]]
            pre_don = self.donors[donor_key]
            if cur_don[1] > pre_don[1]:
                rcpt_key = cur_don[1][:4] + self.cur_in[2] + cur_don[0]
                cur_amt = float(cur_don[2])
            else:
                rcpt_key = pre_don[1][:4] + self.cur_in[2] + pre_don[0]
                cur_amt = float(pre_don[2])
                self.donors[donor_key] = [self.cur_in[0], self.cur_in[3], self.cur_in[4]]
            # check recipient information
            if rcpt_key in self.rcpts:
                pos = self.findInsertPos(self.rcpts[rcpt_key][0], cur_amt)
                self.rcpts[rcpt_key][0] = self.rcpts[rcpt_key][0][:pos] + [cur_amt] + self.rcpts[rcpt_key][0][pos:]
                self.rcpts[rcpt_key][1] = self.rcpts[rcpt_key][1] + cur_amt
            else:
                self.rcpts[rcpt_key] = [[cur_amt], cur_amt]
            # format output stream
            trx_num = len(self.rcpts[rcpt_key][0])
            trx_amt = self.rcpts[rcpt_key][1]
            pctl_pos = math.ceil(self.pct * float(trx_num) / 100.0)
            pctl = self.rcpts[rcpt_key][0][pctl_pos - 1]
            pctl_rd = int(round(pctl))
            if trx_amt.is_integer():
                trx_amt = int(trx_amt)
            self.cur_out = [rcpt_key[9:], self.cur_in[2], rcpt_key[:4], str(pctl_rd), str(trx_amt), str(trx_num)]
            return True
        else:
            self.donors[donor_key] = [self.cur_in[0], self.cur_in[3], self.cur_in[4]]
            return False

#######################################
##### analysis script starts here #####
#######################################
da = DonationAnalysis()
fp_pctl = open(sys.argv[2], 'r')
line = fp_pctl.readline()[:-1]
try:
    float(line)
except ValueError:
    print("percentile file error\n")
    sys.exit()
da.setPercentage(float(line))

useful_cols = [0, 7, 10, 13, 14, 15] # these are the column numbers for needed information based on FEC data format
fp_in = open(sys.argv[1], 'r')
fp_out = open(sys.argv[3], 'w')
line = fp_in.readline()
while line:
    raw_data = line.split('|')
    useful_data = [raw_data[i] for i in useful_cols]
    if da.checkInput(useful_data):
        if da.checkRepeatDonor():
            fp_out.write('|'.join(da.output()) + '\n')
    line = fp_in.readline()
fp_in.close()
fp_out.close()
del da
