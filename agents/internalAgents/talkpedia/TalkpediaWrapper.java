/*package project.searchAnswer;*/

import l2f.dm.answer.provider.AnswerProvider;
import l2f.dm.answer.provider.impl.wiki.WikiAnswerProvider;
import l2f.dm.config.Config;
import l2f.dm.language.generator.AnswerGenerator;
import l2f.dm.language.generator.impl.template.TemplateAnswerGenerator;
import l2f.dm.utils.nlp.sentence.splitter.impl.SimpleSentenceSpliter;
import java.util.Scanner;
/**
 * Answer to questions type IMPERSONAL.
 * 
 * @author CatiaDias
 *
 */
public class TalkpediaWrapper {
	
	
	
	public static void main(String[] args){
		AnswerGenerator ag;
		AnswerProvider ap;
		String configTP = "config_main.xml";
		Config.parseConfig(configTP);
		
		ag = new TemplateAnswerGenerator(configTP);
		ap = new WikiAnswerProvider(Config.wikiURL, Config.maxWikiSearchResults, 
				Config.wikiCache, Config.htmlCache, new SimpleSentenceSpliter(), ag);
		//Scanner user_input = new Scanner( System.in );
		String utterance = "";
		for (String posUtterance : args){
			utterance += posUtterance + " ";
		}
		//System.out.println(utterance);
		utterance = utterance.substring(0, utterance.length() - 1);
		System.out.println(ag.generateAnswer(ap.getAnswer(utterance), utterance, ""));
	}
	
	/*public String getAnswerTP(String posUtterance){
		return ap.getAnswer(posUtterance);
	}*/
	
}
