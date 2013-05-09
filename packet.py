import sys
import re
import datetime

print ""
argc = len(sys.argv)
if (argc == 1):
    print "Invalid number of arguments, a filename is required to run!"
    exit()
elif (argc == 2):
    num = 1
elif (argc == 3):
    num = int(sys.argv[2])
else:
    print "Too many arguments!"
    exit()

expected_packet_num = -1    # 'packet' number of previous line, with range from 0 to 255
line_num = 1
totalLine = 0               # running total of line read in minus time stamps
lostSections = 0            # number of blocks of 'packets' lost
totalLost = 0               # running total of 'packets' lost
time_reset_cnt = 0          # number of times the counter/time is reset/backtacked

try:
    line_num = 1            # current line in the current file
    filename = sys.argv[1]
    file = open(filename, "r")
    file_Data = file.readlines()
    file.close()
except IOError:
    print "ERROR Opening %s" % (filename)
    exit(1)

print "Filename: %s" % (filename)
for data in file_Data:
    # for csv files
    #match = re.split('^\S*\[(\d{3})\],(\d{2}):(\d{2}):(\d{2}).(\d{3})\S*\s', data)
    # for server data
    match = re.split('^\s*\S*\s*\[(\d{3})\]\s*(\d{2}):(\d{2}):(\d{2}).(\d{3})', data)


    if (len(match) == 7):
        current_packet_num = int(match[1])
        current_time = datetime.datetime(2013,                  # year, dummy data
                                         1,                     # month, dummy data
                                         24,                    # day, dummy data
                                         int(match[2]),         # hour
                                         int(match[3]),         # minute
                                         int(match[4]),         # seconds
                                         1000*int(match[5]))    # microseconds

        # First line with packet information
        if (expected_packet_num == -1):
            expected_packet_num = current_packet_num
        # Checking the time diff since last packet
        else:
            time_diff = current_time - prev_time
            time_diff_secs = time_diff.total_seconds()

            if (time_diff_secs < 0):
                time_reset_cnt += 1
                print "\tLine %5d: TIME RESET from %.12s to %.12s" % (line_num, prev_time.strftime("%H:%M:%S.%f"), current_time.strftime("%H:%M:%S.%f"))

                if (time_reset_cnt > 1):
                    reset_time_diff = current_time - prev_time_reset_time
                    reset_time_diff_secs = reset_time_diff.total_seconds()
                    print "\t\tTime since last \'time reset\' = %.f secs" % (reset_time_diff_secs)

                prev_time_reset_time = current_time

        # Check packet number
        diff = current_packet_num - expected_packet_num
        if (diff != 0):
            if (current_packet_num < expected_packet_num):
                diff += 256
            if (diff >= num):
                print "\tline %d: SKIPPED %d packets, %.3f secs have elapsed" % (line_num, diff, time_diff_secs)
                pass
            lostSections += 1

            if (lostSections >1):
                lost_packet_time_diff = current_time - prev_lost_packet_time
                lost_packet_time_diff_secs = lost_packet_time_diff.total_seconds()
                print"\t\tTime since last lost packet(s) = %.f secs" % (lost_packet_time_diff_secs)

            prev_lost_packet_time = current_time
            totalLost += diff
            expected_packet_num = current_packet_num

        if (expected_packet_num != 255):
            expected_packet_num += 1
        else:
            expected_packet_num = 0

        totalLine += 1


        prev_time = current_time

    line_num += 1


print "\nFinished searching through the file. Results:"
print "\t%d sections have been skipped with a total of %d lines" % (lostSections, totalLost)
print "\t%d lines have been read" % (totalLine)
print "\tPacket Loss = %f%%\n" % (100.0*totalLost/(totalLine+totalLost))

print "Time was reset %d times" % (time_reset_cnt)
