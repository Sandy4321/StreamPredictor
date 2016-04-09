# StreamPredictor
Modelling sequential data in way similar to [Hierarchical Hidden Markov Model] (https://en.wikipedia.org/wiki/Hierarchical_hidden_Markov_model) (HHMM). The idea is that every transition from pattern **A** to pattern **B** can itself be modelled as pattern **AB**. 

## Concept ##
Suppose that our collection of pattern consists of {A,B,C,...Z}. i.e. All the Alphabets.Suppose in the first iteration we are given the sequence "CATHAT". 

1. In the first pass we would form patterns like this 
CA, AT, TH, HA, AT. Now our pattern collecton would consists of  {A,B,C,...Z, CA, AT, TH, HA, AT}

2. In the next pass if we encounter the same sequence "CATHAT" we would split the given sequence in terms of largest existing patterns to form the transformed sequence of "CATHAT" = {"CA", "TH", "AT"}. And we would form new patterns by combining 2 at a time the transformed sequence. {{"CATH"}, {"THAT"}}. And so on. 

## Code ##
The given code uses the above concepts for text. 

### Pop ###
Each unit of pattern is called Pop (Pattern of Pattern). It consists of an unrolled pattern which is the complete text representation of the pattern. It uniquely identifies each pop. Each pop also contains two children called first component and second component. 
The following relationship holds 
*Pop.unrolled_pattern = Pop.first_component.unrolled_pattern + Pop.second_component.unrolled_pattern*
Where the + symbol denotes concatenation. 

### Pop Manager ###
Consists of collection of Pops as a dictionary where the keys are the string associated with the Pop.unrolled_pattern and the values are the corresponding Pops.
