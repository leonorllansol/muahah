import java.io.*;
import java.util.*;

public class Selector{
	
	public static void main (String args[]) throws IOException{
		String file1 = "/home/mariana/PycharmProjects/ChaTuga/novo corpora/Treino/questionNonQuestion.txt";
		String file2 = "/home/mariana/PycharmProjects/ChaTuga/novo corpora/Treino/ynQuestion.txt";

		String file11 = "/home/mariana/PycharmProjects/ChaTuga/novo corpora/Treino/questionNonQuestionAnotadores.txt";
		String file22 = "/home/mariana/PycharmProjects/ChaTuga/novo corpora/Treino/ynQuestionAnotadores.txt";

		String keyWord1 = "";
		String keyWord2 = "";
		int counter1 = 0;
		int counter2 = 0;
		String file = "";
		String fileOut = "";
		ArrayList<String> list = new ArrayList<String>();
		ArrayList<String> newList = new ArrayList<String>();
		Random random = new Random();

		System.out.println(args[0]);

		if (args[0].equals("file1")){
			keyWord1 = "QUESTION";
			keyWord2 = "NON_QUESTION";
			file = file1;
			fileOut = file11;
		}
		else if (args[0].equals("file2")){
			keyWord1 = "YN_QUESTION";
			keyWord2 = "OTHER";
			file = file2;
			fileOut = file22;
		}

		FileWriter writer = new FileWriter(fileOut); 

		Scanner s = new Scanner(new File(file));
		
		while (s.hasNext()){
		    list.add(s.nextLine());
		}
		s.close();

		while (counter1 <= 50 || counter2 <=50) {
			int randomNumber = random.nextInt(list.size());
			String line = list.get(randomNumber) + "\n";
			System.out.println(counter1 + " outro " + counter2 + " linha " + line + " rando " + randomNumber);
			if (newList.indexOf(line) == -1){

				if (line.indexOf(keyWord2) != -1 && counter2 <= 50){
					counter2++;
					newList.add(line);
					writer.write(line);
					list.remove(line);
				}
				else if (line.indexOf(keyWord1) != -1 && counter1 <= 50){
					counter1++;
					newList.add(line);
					writer.write(line);
					list.remove(line);
				}


			}
		}
		writer.close();
	}
}