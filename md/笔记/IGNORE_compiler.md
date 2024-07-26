

### top-down parsing
#### 算法1：recursive descent parsing

#### 算法2：predictive parsing
- left factor：消除左公共因子。
- first set：指文法中所有可能出现在一个产生式右侧的终结符号集合。它的作用是用于预测在分析过程中，下一个输入符号是否可以被当前的非终结符号推导出来。
- follow set：指文法中某个非终结符号在右侧可能出现的终结符号集合。它的作用是用于预测在规约过程中，需要向前看多少个输入符号。
- parsing table：构建parsing table时，产生非空串的，看first set（如，Y->X|+，则要看Y的first set）；可产生非空串的，除了看first set，还要看follow set（如，Y->X|+|ε）。

> 快速检查是否为LL（1）：不是left factored的语法不是LL（1）；left recursive的语法不是LL（1）；有歧义的语法不是LL（1）；（以上为不是LL（1）的充分条件）

### bottom-up parsing
#### shift-reduce parsing
#### handle
#### Recognizing Viable Prefixes，Nondeterministic Finite Automaton（NFA）
#### valid items

#### SLR，Simple LR Parsing（利用了Recognizing VP和Valid items）
> Refer to the DFA to determine the appropriate move to make. Remember that a reduce move will only be made if the next symbol in the input is in the follow set of the reduced symbol. An accept move is only made if we reach the start symbol and there is no further input to consume.