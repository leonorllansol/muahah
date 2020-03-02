# chatuga-sss

## What is it?

Say Something Smart (SSS) is a dialogue engine based on a large corpus of movie subtitles (Subtle). 

This specific project - chatuga-SSS - is focused on the implementation of a plug-and-play system composed by multiple distinct agents: each agent gives its own response to the received user input, and the best answer is reached through a set of different decision making strategies.


## How does it work?

Upon receiving input from the user, SSS retrieves the most similar candidates (that is, entries of the Subtle corpus) through Whoosh and sends both the user query and the candidates to all available agents. Subsequently, each agent gives its own answer to the query, and the best answer is delivered to the user.

This process is accomplished through the use of four modules:
- The `DocumentManager` module, which indexes the Subtle corpus and allows the other SSS modules to retrieve the best candidates to a query.
- The `AgentHandler` module, which initializes all of the agents and, upon receiving a user query, delivers the necessary information (query, candidates) to each agent. It also stores the answers of each agent.
- The `Decisor` module, which receives the answers generated by the AgentHandler modules and sends them to each decision making strategy. Each strategy returns an answer.
- The `Boss` module, which is the main module of this project. It receives a user query, sends it to the AgentHandler, and sends the given answers to the Decisor module, which returns an answer by strategy. The Boss then chooses which answer to return to the user, based on the confidence it has on each strategy.


## Getting started
  ### Requirements: 
  - Python3 
  - The two following commands will install all the requirements for this project
  - `pip install requirements.txt` 
  - `python3 -m spacy download pt_core_news_sm`
  - Execute the following to install some nltk dependencies:
  - `python3`
  - `>>> import nltk`
  - `>>> nltk.download('wordnet')`
  - `>>> nltk.download('omw')`
  - Finally, to run the program, execute the command `python3 boss.py`. The program will prompt you with "Diga algo: ", after which you can type your query.
  - When you desire to end the interaction, type `exit`.
  
  
## Adding a new agent:
  - An external agent is defined by two components: the configuration file, and the source code.
  - The configuration file serves as the header of the agent, allowing it to be detected and added to the pool of available agents. It also allows the user to set configurable parameters without directly interacting with the source code. Each agent has its own configuration file.
  - The source code of the agent is composed by one or more source files, whose goal is to deliver an answer upon receiving a user query (and, optionally, a set of candidates).
  ### 1. Adding the new agent to the project's configuration files
  - Agents can be activated and deactivated in the config.xml file:
  `<agents>
     <agent name="JaccardAgent" active="1"/>
     <agent name="LevenshteinAgent" active="0"/>
  </agents>`
  In the previous example, JaccardAgent is activated, while LevenshteinAgent is deactivated, so the latter will not be instantiated not will it return an answer.
  - Each agent can have labels associated to it, for example:
    - QUESTION - agent is good at answering questions
    - NON_QUESTION - agent is good at answering non questions
    - YN_QUESTION - agent is good at answering yes/no questions
    - PERSONAL - agent is good at answering personal questions
  - If the agent does not have a particular domain associated, you can just assign it with the QUESTION and NON_QUESTION labels.
  `<externalAgent name="YesNoAgent">
		<labels>
			<label score='1.0'>QUESTION</label>
			<label score='1.0'>YN_QUESTION</label>
		</labels>
	</externalAgent>`
  ### 2. Paths and Directories
  Before you start building your new agent, you should know where it should be placed in order to be found by chatuga-SSS.
  For the context of building agents, the folder structure of chatuga-SSS is as follows:
  `chatuga-sss
    └── agents
        └── externalAgents
            └── Agent1
                ├── config.xml
                └── Agent1.py
            └── Agent2
                ├── config.xml
                └── Agent2.py
`
  When creating a new agent, the directory containing the source code and config file of the agent should be inside the `externalAgents` folder, and the configuration file of the agent **must** be named `config.xml`.
  ### 3. Configuration file
  When creating the `config.xml` file for your agent, you should follow the structure below:

    <config>
        <mainClass>agentName</mainClass>
        (other parameters to define)
        (...)
    </config>

All defined parameters must be encapsulated by the exterior tag `<config>`, and the `<mainClass>`must be defined with the same name as the main class of the agent.
  ### 4. Source Code
  As mentioned before, an agent can have more than one source file, but it must have a **main** source file. The main file usually has the same name as the agent's folder, and it corresponds to the connection point between chatuga-sss and the agent.

That said, the following indications must be followed when creating a new agent:

- The agent's main file must be implemented as a `class`;
- The agent's class must implement the function `requestAnswer(self,userInput,candidates)`, which receives a `userInput` string and a `candidates` array, and must return an `answer` string.

- `userInput` is a string that contains a query made directly to SSS by the user (e.g.: "Como te chamas?").
- `candidates` is an array containing the generated candidates for the above user query in the format `[CandidateObject1, CandidateObject2, ... , CandidateObjectN]`. Candidate objects correspond to instances of the `SimpleQA` class, found in:

        chatuga-sss
        └── dialog
            ├── BasicQA.py
            └── SimpleQA.py
  
## Adding a new Decision Making Strategy:
  - Given a set of answers, a Decision Making Strategy chooses one of them, according to its heuristics. For example, SimpleMajority chooses the most given answer, and YesNoStrategy chooses an answer which contains "yes" or "no".
  - 1. A decision making strategy can be implemented in a single file: in folder decisionMakingStrategies, create a new subclass of DecisionMethod. This class **must** have a method getAnswer, which returns an answer.
  - 2. Add the name of the new class and corresponding class and arguments to, respectively, the dictionaries all_strategies and args_by_strategy of Decisor.py.
  - 3. add it to the config.xml file (tag `<decisionMethod>`) and give it a weight, considering that all weights must sum to 100.
  
## Project configurations
  - There are three files for project configurations, all in the config folder: config.xml, agents_config.xml and corpora_config.xml.
  - config.xml: this is the overall project configuration file. It contains all agents and whether they are active or not, as seen in section "Adding a new agent"; it contains the existing decision making strategies and corresponding weights. It also contains the tag `<corpusPath>`, where the corpus to use is defined. **NOTE**: if you add a new corpus, new whoosh indexes will be created, which may take a long time if the corpus is large (SubTle has 19 million lines and took about 9 hours).
  - agents_config.xml: this file contains the labels associated to each agent.
  - corpora_config.xml: this file contains information about the corpora used in this project.

 