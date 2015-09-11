
import re, fileinput
from statistics import *

av_score_re = re.compile("AUDIO: (.*?)VIDEO: ([0-9]+)")


def main():
	score = []
	audio = []
	video = []
	count = 0
	for line in fileinput.input():
		match = av_score_re.findall(line)
		if(match):
			audio.append(int(match[0][0]))
			video.append(int(match[0][1]))
			count += 1

	#audio_avg = audio / count
	#video_avg = video / count

	print()
	print("# of entries : %4.0f" % (count))
	print("-" * 30)
	print("average: arithmetic mean")
	print("audio: %4.2f" % (mean(audio)))
	print("video: %4.2f" % (mean(video)))
	print("-" * 30)
	print("median: middle value")
	print("audio: %4.0f" % (median(audio)))
	print("video: %4.0f" % (median(video)))
	print("-" * 30)
	print("mode: most common value")
	try:
		a = mode(audio)
	except StatisticsError:
		a = -1.0
	try:
		v = mode(video)
	except StatisticsError:
		v = -1.0
	print("audio: %4.0f" % (a))
	print("video: %4.0f" % (v))
	print("-" * 30)
	print("measures of spread")
	print("std dev : audio: %4.2f  video: %4.2f" % (pstdev(audio), pstdev(video)))
	print("variance: audio: %4.2f  video: %4.2f" % (pvariance(audio), pvariance(video)))
	print()

main()
