# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

class DataAnal():
    
    def __init__(self):
        self.data_base = {}
        self.repeat_donor = {}
        self.cur_input = []
        self.cur_output = []
        self.percentile = 0
    
    def findInsertPosition(self, num_hist, num):
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
        return l
    
    def setPercentile(self, percentile_value):
        self.percentile = percentile_value
    
    def checkInput(self, input_data):
        """
        check if input_data is valid based on content of 'Input file considerations' from instruction
        input_data should be listed in the order of [CMTE_ID, NAME, ZIP_CODE, TRANSACTION_DT, TRANSACTION_AMT, OTHER_ID]
        """
        # input : list of string which contains input data
        # output : False if input is invalid can be ignored; True if input is valid
        #### check length for all properties
        if len(input_data[0]) == 0 or len(input_data[1]) == 0 or len(input_data[2]) < 5 or len(input_data[3]) != 8 or len(input_data[4]) == 0 or len(input_data[5]) > 0:
            return False
        #### check NAME, NAME should only contain letters, space, comma or period
        for c in input_data[1]:
            if not (c == ',' or c == ' ' or c == '.' or c.isalpha()):
                return False
        #### check ZIP_CODE, ZIP_CODE should only contain digits
        for x in input_data[2]:
            if not x.isdigit():
                return False
        input_data[2] = input_data[2][:5]
        #### check TRANSACTION_DT, date should only contain digits, and follow date constrains
        for x in input_data[3]:
            if not x.isdigit():
                return False
        month = int(input_data[3][:2])
        day = int(input_data[3][2:4])
        year = int(input_data[3][4:])
        if month > 12 or month == 0 or day > 31 or day == 0 or year < 2000 or year > 2018:
            return False
        #### TRANSACTION_AMT, amount should be able to be converted to float
        try:
            float(input_data[4])
        except ValueError:
            return False
        self.cur_input = input_data[:-1].copy()
        return True
        
    def checkRepeatDonor(self):
        cur_key_input = self.cur_input[2] + self.cur_input[1]
        if cur_key_input in self.data_base:
            cur_year = self.cur_input[3][4:]
            pre_year = self.data_base[cur_key_input][1][4:]
            if int(cur_year) > int(pre_year):
                cur_key_output = cur_year + self.cur_input[0]
                cur_amt = float(self.cur_input[4])
            else:
                self.data_base[cur_key_input] = [self.cur_input[0], self.cur_input[3], self.cur_input[4]]
                cur_key_output = pre_year + self.cur_input[0]
                cur_amt = float(self.data_base[cur_key_input][2])
                
            if cur_key_output in self.repeat_donor:
                insert_pos = self.findInsertPosition(self.repeat_donor[cur_key_output][0], cur_amt)
                self.repeat_donor[cur_key_output][0] = self.repeat_donor[cur_key_output][0][:insert_pos] + [cur_amt] + self.repeat_donor[cur_key_output][0][insert_pos:]
                self.repeat_donor[cur_key_output][1] = self.repeat_donor[cur_key_output][1] + cur_amt
            else:
                self.repeat_donor[cur_key_output] = [[cur_amt], cur_amt]
            
            transaction_num = len(self.repeat_donor[cur_key_output][0])
            transaction_amt = self.repeat_donor[cur_key_output][1]
            percentile_pos = (self.percentile / 100.0) * transaction_num
            percentile_nearest_rank = int(percentile_pos)
            if percentile_nearest_rank < percentile_pos:
                percentile_nearest_rank = percentile_nearest_rank + 1
            running_percentile = self.repeat_donor[cur_key_output][0][percentile_nearest_rank - 1]
            percentile_round = int(running_percentile)
            if running_percentile - percentile_round >= 0.5:
                percentile_round = percentile_round + 1
            self.cur_output = [cur_key_output[4:], cur_key_input[:5], cur_key_output[:4], str(percentile_round), str(transaction_amt), str(transaction_num)]
            
            return True
        else:
            self.data_base[cur_key_input] = [self.cur_input[0], self.cur_input[3], self.cur_input[4]]
            return False
    
    def output(self):
        return self.cur_output

da = DataAnal()
da.setPercentile(30.0)
fp_input = open('./test.txt', 'r')
fp_output = open('./repeat_donors.txt', 'w')
useful_cols = [0, 7, 10, 13, 14, 15]
line = fp_input.readline()
while line:
    raw_data = line.split('|')
    useful_data = [raw_data[i] for i in useful_cols]
    if da.checkInput(useful_data):
        if da.checkRepeatDonor():
            tmp = da.output()
            fp_output.write('|'.join(tmp) + '\n')
    line = fp_input.readline()
fp_input.close()
fp_output.close()