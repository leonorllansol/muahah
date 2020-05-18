import subprocess
import sys

def inquiry(query):
	listArgs = ['java','-cp', 'jsoup-1.12.2.jar:commons-text-1.8.jar:jdom.jar:commons-io-2.6.jar:commons-lang3-3.9.jar:.', 'TalkpediaWrapper', query]
	listAnswers = []
	
	sp1 = subprocess.Popen(listArgs, shell=False, stdout=subprocess.PIPE)
	#while True:
#		line = sp1.stdout.readline()

#		if not line:
#			break
  #the real code does filtering here
		#print("test:", line.rstrip())
	answer1 = sp1.stdout.read().decode('utf-8')
	#print(answer1)
	#answer1 = "Uma cantora."
	return answer1


if __name__ == "__main__":
	inquiry(sys.argv)