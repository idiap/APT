## Description

A reference-based metric to evaluate the accuracy of pronoun translation (APT).

## Requirements:


python 2.7.* (https://www.python.org/downloads/)


## Command:

```
python APT.py [configuration file]
```

## Example:

There is an example in the following folder.

    data_es-en


The configuration file  is called "config_*". Basically it needs the source, reference and target files as well as the alignments source-reference and source-target in Moses format. 

The alignment source-reference can be done with Moses trainning steps 1,2,3. For now the alignment is not in the script of APT.

```
cd [path-to-APT]/APT.V.4
python APT.py ./data_es-en/config_1
```

The output will be in ./data_es-en/output1

## Reference:

>@inproceedings{miculicich2017validation,
>  title={Validation of an Automatic Metric for the Accuracy of Pronoun Translation (APT)},
>  author={Miculicich Werlen, Lesly and Popescu-Belis, Andrei},
>  booktitle={Proceedings of the Third Workshop on Discourse in Machine Translation (DiscoMT)},
>  number={EPFL-CONF-229974},
>  year={2017},
>  organization={Association for Computational Linguistics (ACL)}
>}
 
## Contact:

lmiculicich@idiap.ch
