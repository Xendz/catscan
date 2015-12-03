import core
import random

b = core.Bot('irc.blackcatz.org', 6697, "blackcat-{}".format( str( random.choice( range( 1, 1001 ) ) ) ), 'sc0uts', 'sc0sut', 'sc0ust', True)

b.run()


