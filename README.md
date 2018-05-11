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
```
@inproceedings{miculicich2017validation,
  title={Validation of an Automatic Metric for the Accuracy of Pronoun Translation (APT)},
  author={Miculicich Werlen, Lesly and Popescu-Belis, Andrei},
  booktitle={Proceedings of the Third Workshop on Discourse in Machine Translation (DiscoMT)},
  number={EPFL-CONF-229974},
  year={2017},
  organization={Association for Computational Linguistics (ACL)}
}
``` 
## See also:
Gonzales, Annette Rios, and Don Tuggener. ["Co-reference Resolution of Elided Subjects and Possessive Pronouns in Spanish-English Statistical Machine Translation"](http://www.aclweb.org/anthology/E17-2104). Proceedings of the 15th Conference of the European Chapter of the Association for Computational Linguistics. 2017.

Luong, Ngoc-Quang, and Andrei Popescu-Belis. ["Machine translation of Spanish personal and possessive pronouns using anaphora probabilities"](http://www.aclweb.org/anthology/E17-2100). Proceedings of the 15th Conference of the European Chapter of the Association for Computational Linguistics. 2017.

Miculicich Werlen, Lesly, and Andrei Popescu-Belis. ["Using coreference links to improve spanish-to-english machine translation"](http://www.aclweb.org/anthology/W17-1505). Proceedings of the 2nd Workshop on Coreference Resolution Beyond OntoNotes. 2017.

## Contact:

lmiculicich@idiap.ch
