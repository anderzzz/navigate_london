from agent import agent_router

x = agent_router.process('Conversation started')
print (x)
x = agent_router.process('I am an avid biker. I always want to bike when possible. So please consider all further requests with that in mind.')
print (x)
