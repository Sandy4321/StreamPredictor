# StreamPredictor
We try to model sequential structured data like natural text using a combinatino of Hierarchical Patterns and Evolution. 
The aim is to get a probabilistic, language independent model for sequential data. 
During training we learn which pattern comes after each pattern similar to a bigram. 
Then each transition from pattern to pattern is made as a new pattern.
Many spurious patterns are formed but only ones that are repeated are retained. Performance is calculated by measuring the perplexity for words from some Enlgish novels.

More details are given here [Paper](https://www.researchgate.net/publication/301594438_Hierarchical_evolutionary_sequence_patterns)

# Concepts
## Hierarchical Pattern Formation
The main concept used is somewhat similar to [Hierarchical Hidden Markov Model] (https://en.wikipedia.org/wiki/Hierarchical_hidden_Markov_model) (HHMM). The idea is that every transition from pattern **A** to pattern **B** can itself be modelled as pattern **AB**. But the inference method is different.

Suppose that our collection of pattern consists of {A,B,C,...Z}. i.e. All the Alphabets.Suppose in the first iteration we are given the sequence "CATHAT". 

![Pattern of Patterns image][logo]
[logo]: docs/pop.png "Pattern of patterns"

1. In the first pass we would form patterns like this 
CA, AT, TH, HA, AT. Now our pattern collecton would consists of  {A,B,C,...Z, CA, AT, TH, HA, AT}

2. In the next pass if we encounter the same sequence "CATHAT" we would split the given sequence in terms of largest existing patterns to form the transformed sequence of "CATHAT" = {"CA", "TH", "AT"}. And we would form new patterns by combining 2 at a time the transformed sequence. {{"CATH"}, {"THAT"}}. And so on. 

## Evolution of Patterns
With the above formation lots of spurious patterns will be formed. We need to keep only useful patterns and discard unused ones. So Every time we encounter a pattern we "feed" it and it's strength increases. Strength is just an integer number associated with each pattern. As time increases we decrement strength of all patterns. If strength falls below certain threshold we cull the patterns. Hence patterns that are not repeated will die out. Also when we feed a pattern it's children are also given a share. It is essential that all formed pattern are given sufficient time before being killed as they maybe useful later on as children of other more complicated patterns.

#Demo 
The demo is given in this [notebook](https://github.com/abhishekraok/StreamPredictor/blob/master/notebook/LanguageDemo.ipynb).

# Code
The given code uses the above concepts for text. 

### Pop
Each unit of pattern is called Pop (Pattern of Pattern). It consists of an unrolled pattern which is the complete text representation of the pattern. It uniquely identifies each pop. Each pop also contains two children called first component and second component. 
The following relationship holds 
*Pop.unrolled_pattern = Pop.first_component.unrolled_pattern + Pop.second_component.unrolled_pattern*
Where the + symbol denotes concatenation. 

### Pop Manager
Consists of collection of Pops as a dictionary where the keys are the string associated with the Pop.unrolled_pattern and the values are the corresponding Pops.

Some of the methods of this class are 

1. *Train()* Takes a string as input and trains the model. Essentialy forms a collection of patterns.
2. *Generate()* Using the patterns collection generates a stream of likely text. 




