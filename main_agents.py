from agent import agent_router

#x = agent_router.process('Conversation started')
#print (x)
#x = agent_router.process('I am an avid biker. I always want to bike when possible. So please consider all further requests with that in mind.')
#print (x)
x = agent_router.process('I wish to go from a stop in London with the code 490000119F to a stop with the code 490000040A on 11th November departing at six in the evening. Include at least one very bike centric route, so to speak')
print (x)
x = agent_router.process('Well then, show me the details of that third plan with biking!')
print (x)
