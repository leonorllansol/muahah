from DefaultAnswers import HighestWeightedScoreSelection, MultipleAnswerSelection
import logging, sys, time
import configParser, subprocess
from DecisionMaker import DecisionMaker
from AgentManager import AgentManager
import discord
import json
from discord.ext import commands
from discord.ext.commands import Bot
import TokenEng
from discord import utils
import DocumentManager



defaultAgentsMode = configParser.getDefaultAgentsMode()

if(not configParser.usePreviouslyCreatedIndex()):
    DocumentManager.createIndex(configParser.getIndexPath(), configParser.getCorpusPath()) 
    
    
        
bot = Bot(command_prefix='~')

    
authChannels = [460565759945342987,613926491004076042]

    
multipleAnswerSelection = MultipleAnswerSelection()
agentManager = AgentManager()
decisionMaker = DecisionMaker(configParser.getDecisionMethod())
cachedMessages = {}
cachedMessagesCount = 0


@bot.event
async def on_ready():
    for server in bot.guilds:
        cachedMessages[server.id] = []


@bot.event
async def on_message(message):
    global cachedMessagesCount
    if(not message.author.bot and message.channel.id in authChannels):

        query = message.content


        logging.basicConfig(filename='log_edgar_' + time.strftime('%d%m%Y_%H%M%S') + '.txt', filemode='w', format='%(message)s', level=logging.INFO)
        logging.info("Query: " + query)
        print(query)
        

        #defaultAgentsAnswers = multipleAnswerSelection.provideAnswer(query)
        defaultAgentsAnswers = {}

        externalAgentsAnswers = agentManager.generateAgentsAnswers(query)
        # Both defaultAgentsAnswers and externalAgentsAnswers are dictionaries in the format {'agent1': 'answer1', 'agent2': 'answer2'}
        

        # Calling the DecisionMaker after having all of the answers stored in the above dictionaries
        answer = decisionMaker.decideBestAnswer(defaultAgentsAnswers,externalAgentsAnswers)


        logging.info("\n")
        logging.info("Query: " + query)
        logging.info("Final Answer: " + answer)


        print("Question:", query)
        print("Final Answer:", answer)
        print()

        sentMessage = await message.channel.send(answer)
    

        # Create interaction dict for .json file and store it in the cachedMessages array

        interaction = {"query": query, "answer": answer, "userID": message.author.id, "posReacts": 0, "negReacts": 0, "midReacts": 0, "timestamp": time.time(), "messageID": sentMessage.id, "serverID": message.guild.id}

        cachedMessages[message.guild.id].append(interaction)
        cachedMessagesCount += 1

        if(cachedMessagesCount > 50):
            data = {'sequences': []}
            currentSequence = []
            for elInteract in cachedMessages[message.guild.id]:
                if(len(currentSequence) == 0):
                    currentSequence.append(elInteract)
                elif(elInteract["posReacts"] < elInteract["negReacts"] or elInteract["timestamp"] - currentSequence[-1]["timestamp"] > 300):
                    data['sequences'].append(currentSequence)
                    currentSequence = []
                    currentSequence.append(elInteract)
                else:
                    currentSequence.append(elInteract)
                    
                print(elInteract["query"] + "||||" + elInteract["answer"])
                #cachedMessages[message.guild.id].remove(elInteract)
            
            
            data['sequences'].append(currentSequence)
            currentSequence = []

            with open("learningAgentData.json", "w") as output:
                print(data)
                json.dump(data, output)

            cachesMessages[message.guild.id] = []
            cachedMessagesCount = 0


    elif(message.author.id == bot.user.id):
        if(configParser.getAnswerAmount() == 1):
            await message.add_reaction('✅')
            await message.add_reaction('❌')
            await message.add_reaction('❔')
        elif(configParser.getAnswerAmount() > 1):
            emoji = ["1⃣","2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣"]
            for i in range(0,configParser.getAnswerAmount()):
                await message.add_reaction(emoji[i])

    await bot.process_commands(message)



@bot.event
async def on_reaction_add(reaction,user):
    serverID = reaction.message.guild.id
    messageID = reaction.message.id
    interaction = {}
    for elInteract in cachedMessages[serverID]:
        if(elInteract["messageID"] == messageID):
            interaction = elInteract
            break
    if(interaction != {}):
        if(str(reaction) == '✅'):
            print("rated positive")
            interaction["posReacts"] += 1
        elif(str(reaction) == '❌'):
            print("rated negative")
            interaction["negReacts"] += 1
        elif(str(reaction) == '❔'):
            print("rated ???")
            interaction["midReacts"] += 1




@bot.event
async def on_reaction_remove(reaction,user):
    serverID = reaction.message.guild.id
    messageID = reaction.message.id
    interaction = {}
    for elInteract in cachedMessages[serverID]:
        if(elInteract["messageID"] == messageID):
            interaction = elInteract
            break
    if(interaction != {}):
        if(str(reaction) == '✅'):
            print("disrated positive")
            interaction["posReacts"] -= 1
        elif(str(reaction) == '❌'):
            print("disrated negative")
            interaction["negReacts"] -= 1
        elif(str(reaction) == '❔'):
            print("disrated ???")
            interaction["midReacts"] -= 1





bot.run(TokenEng.token)