#!/usr/bin/python

import infix2postfix
import simulation
import copy

# Conversion of regular expressions into NFA
regexFile = file("../../test/input1","r")


# move = { state:{ input:(List of states) , input:(List of states) , ... }  , ... }


NFAList = {}  # List of base NFA's constructed. {"regex":NFA_Class_Object, ... }
NFAall_List	= []     # Regex OR applies to all the individual regular expressions.

# NFA Structure
class NFA(object) :
	def __init__(self):
		self.regex = ''    # Regex that it represents.
		self.s0 = 0        # Start State
		self.F = set()     # Set of accepting states
		self.move = {}     # Two dimensional transition table
		self.nos = 0       # Number of states
		self.token = ''    # Token Name

def inc_states(nfa,base):	# base is the number to start with.
	nfa_new = NFA()
	nfa_new.regex = nfa.regex	# The regex is same for both.
	nfa_new.s0 = base		# The start state is incremented by the base.
	nfa_new.nos = nfa.nos
	
	# The list of final states is incremented by the base no.
	for final in nfa.F :
		nfa_new.F.add(final + base)
	
	for key in nfa.move.iterkeys() :
		# nfa.move[key] is again a dictionary like {input:(set of states),input:(set of states), ... }
		nfa_new.move[key + base] = {}
		for symbol in nfa.move[key].iterkeys() :
			nfa_new.move[key + base][symbol] =  set()
			# nfa.move[key][symbol] is a set of states.
			for states in nfa.move[key][symbol] :
				nfa_new.move[key + base][symbol].add(states + base)
	return nfa_new




# Implementation MYT (McNaughton-Yamada-Thompson) Algorithm
def NFA_MYT(NFA_1,NFA_2,op) :
	
	# This would require a state re-numbering.
	NFA_final = NFA()
	NFA_3 = NFA()         # NFA_3 is obtained through state re-numbering on NFA_2
	# NFAList[NFA_final.regex] = NFA_final
	
	
	
	if op == '|' :
		NFA_final.regex = NFA_1.regex + op + NFA_2.regex
		NFA_final.nos = NFA_1.nos + NFA_2.nos + 2
		NFA_3 = inc_states(NFA_2,NFA_1.nos)
		NFA_3.s0 = NFA_2.s0 + NFA_1.nos
		# Now comes the part of MYT algorithm
		NFA_final.s0 = NFA_final.nos - 2        # New start state
		NFA_final.F.add(NFA_final.nos - 1)	# New Single Final state

		# epsilon-transitions from the new start state to the start states of the two NFA's under the or operation
		NFA_final.move[NFA_final.s0] = {'#' : set([NFA_1.s0, NFA_3.s0])}
		
		
		# epsilon-transitions from the final states of the two NFA's under the or operation to the new final state.
		for final in NFA_1.F :
			NFA_final.move[final] = {'#' : copy.copy(NFA_final.F)}  # Shallow copy
		for final in NFA_3.F :
			NFA_final.move[final] = {'#' : copy.copy(NFA_final.F)}         # Shallow copy
		
		# Now add the other transitions from NFA_1 and NFA_3 to NFA_final
		NFA_final.move.update(NFA_1.move)
		NFA_final.move.update(NFA_3.move)


	elif op == '%' :
		# NFA_2 is 'i' and NFA_1 is 'f'
		NFA_final.regex = NFA_2.regex + op + NFA_1.regex
		NFA_final.nos = NFA_1.nos + NFA_2.nos
		NFA_3 = inc_states(NFA_1,NFA_2.nos)
		NFA_3.s0 = NFA_1.s0 + NFA_2.nos
		# Now comes the part of MYT algorithm

		NFA_final.s0 = NFA_2.s0         # The start state of the new NFA is same as the start state of the first NFA under concatenation.
		NFA_final.F = copy.copy(NFA_3.F)           # The set of final states for the new NFA is the same as the set of Final states of the 2nd NFA under concatenation.

		
		# Now add the other transitions from NFA_1 and NFA_3 to NFA_final
		NFA_final.move.update(NFA_2.move)
		NFA_final.move.update(NFA_3.move)
		

		# epsilon-transitions to the final states of the two NFA's under the or operation to the new final state.
		for final in NFA_2.F :
			NFA_final.move[final] = {}
					
		for final in NFA_2.F :
			NFA_final.move[final]['#'] = set()
			
		for final in NFA_2.F :
			NFA_final.move[final]['#'].add(NFA_3.s0)
		print NFA_2.move
		print NFA_3.move
		print NFA_final.move
	
	elif op == '*' :
		# Here, no renumbering of states is allowed.
		
		NFA_final.regex = NFA_1.regex + op
		NFA_final.nos = NFA_1.nos + 2
		
		# Now comes the part of MYT algorithm
		NFA_final.s0 = NFA_final.nos - 2		# New start state
		NFA_final.F.add(NFA_final.nos - 1)		# New Single Final state

		NFA_final.move[NFA_final.s0] = {}
		#NFA_final.move[NFA_final.s0]['#'] = set()
		
		# START STATE
		NFA_final.move[NFA_final.s0]['#'] = copy.copy(NFA_final.F)
		NFA_final.move[NFA_final.s0]['#'].add(NFA_1.s0)
		
		# OLD FINAL STATES
		for final in NFA_1.F :
			NFA_final.move[final] = {}
			NFA_final.move[final]['#'] = copy.copy(NFA_final.F)
			NFA_final.move[final]['#'].add(NFA_1.s0)
		
		
		NFA_final.move.update(NFA_1.move)


		#print NFA_1.move
		#print op
		#print NFA_final.move
	
	return NFA_final			


# Constructs the base NFA's form the given Postfix regex expression to be used for the base cases in the MYT algorithm
# Also uses the global NFAList to see if a given conversion of regex to NFA already exists or not.

def regex_NFA_base(char):
	if NFAList.has_key(char) :
		return NFAList[char]
	else :
		nfa = NFA()
		nfa.nos = 2
		nfa.regex = char
		NFAList[nfa.regex] = nfa
		nfa.F.add(1)
		nfa.move[nfa.s0] = {char : copy.copy(nfa.F)}	# Shallow copy
		return nfa


# Converts all the operands in the postfix regex into base NFA's
def Regex2NFA(postfix) :
	NFA_postfix = []	# Empty list consists of base NFA's used for MYT Algorithm
	i = 0
	length = len(postfix)
	nfa = NFA()
	while (i < length) :
		if (postfix[i] <> '*' and postfix[i] <> '|' and postfix[i] <> '%' and postfix[i] <> '.') :
			# It's an operand
			if ( postfix[i] == '\\' ) :
				# We just encountered an escaped operand
				nfa = regex_NFA_base(postfix[i + 1])
				
				NFA_postfix.append(nfa)
				i = i + 1
			
			else :	# It's a non escaped character
				nfa = regex_NFA_base(postfix[i])
				NFA_postfix.append(nfa)
		else :

			# It's an operator
			NFA_postfix.append(postfix[i])
				
		i = i + 1	# iterator
	return NFA_postfix



# Finally evaluates the NFA Postfix expression to output the Cumulative NFA using the function NFA_MYT()

def postfixEval(postfix) :	# Postfix evaluator . ***** ALL OPERANDS IN THIS POSTFIX EXPRESSION ARE NFA's *****
	operandStack = []	# Empty list ( These are heterogeneous )
	length = len(postfix)
	i = 0
	top0 = ''
	top1 = '' 
	nfa = NFA()
	while ( i < length ) :
		if ( postfix[i] <> '*' and postfix[i] <> '|' and postfix[i] <> '%' ) :
			# Implies this is an operand
			operandStack.append(postfix[i])
	
		else : # It's an operator
			top0 = operandStack.pop(len(operandStack) - 1)
			if ( postfix[i] == '*' ) :	# Unary operator
				nfa = NFA_MYT(top0,None,postfix[i])
				
			else :	
				top1 = operandStack.pop(len(operandStack) - 1)
				nfa = NFA_MYT(top0,top1,postfix[i])
		
			operandStack.append(nfa)
		i = i + 1	# iterator


	return operandStack.pop(len(operandStack) - 1)			


# List of all the NFA's constructed using the MYT Algorithm from the input list of regular expressions
NFA_Lex = []	# Empty List


def build_NFA():
	global NFAall
	for nextLine in regexFile :
		nextLine = nextLine.splitlines()[0] # Strip the new line character at the end of string.
		words = nextLine.split('\t')
		regex = words[0]
		token = words[1]
		postfix = infix2postfix.infix2postfix(regex)
		NFA_postfix = Regex2NFA(postfix)
		nfa = postfixEval(NFA_postfix)
		nfa.token = token	# Updating the token name
		NFAall_List.append(nfa)
		print "******************************************" + " TRANSITION TABLE for  " + str(nfa.regex) + "  ***********************************************"
		for key in nfa.move.iterkeys() :
			print nfa.move[key]
		print "******************************************************************************************************************************************"




if __name__ == '__main__' :
	
	build_NFA()
	simulation.NFA_simulate(NFAall_List)


	


