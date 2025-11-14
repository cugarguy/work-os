# Q AI Best Practices

*Captured: 2025-11-14 15:12*

**Notes about Q:**
	The easy 20% that Q is good at
		get me the logs for all the servers from time to time
		did these servers have any CRIT logs in last hour
			Then filter those with another field
		use jq to understand the structure of json
			get me the list of all the test without "options"
	Tips
		don't bother writing nicely, typos, phrasing, etc
		don't tell it too many things to do max2
		if it doesn't do what want - CTRL-C
		Don't ask for reasons 
		if you run out of context - kill and start again
			write to temp files
		kill Q between tasks
			Q thinks everything in same session is related
		Tell it not to read files when they are big
		Dont' expect it too much
	Examples
		what is the ip in the ticket - good
		read the log and tell me why it failed - bad
		REad the test log tell me ip
			get me the ip from the test log instead
30% - Small Prompts
	repeatable tasks - the ones you really don't like to do
Example:
1. I am going to teach you how to handle a new flow. Don't take actions unless I tell you to
2. read this ticket https://sim.amazon.com/issues/EBS-265853
3. if we found nothing - stop here and tell the user this does not look like hydration issue. If we found anything run on the ip we found the cnd ebscliip>
4. write everything we learaned so far to a prompt file so we can rerun it on other tickets
5. load ebs_stuck_volume_investigation_flow.md quietly and handle https://sim.amazon.com/issues/EBS-265853
How to start again
	save flow to prompt file
	load prompt file
	--resume 
Tell q you are in teaching mode and to not take any free steps or actions
Tell Q to write the prompt
	IF it has several parts - let Q write it then tell it to edit it
	Don't let Q add wrong reasons
	The more complex the flow is and the more freedom you give Q - the more likely it is to make mistakes
Trust and Q
- The closer it is to copy-paste the more trust you can give Q
- ﻿﻿When it become "flow-chart" like - Q can make mistakes
- ﻿﻿Q will give a reason to anything it sees. This reason is often not correct
- ﻿﻿I can't trust Q to always remember to run a query
- ﻿﻿I can trust it when it tells me it run it and got X
- ﻿﻿Q had a hard time ignoring data
- Q really want you to be right - so it will look for reasons
