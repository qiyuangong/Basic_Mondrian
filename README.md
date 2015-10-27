Basic Mondrian
===========================
Mondrian is a Top-down greedy data anonymization algorithm for relational dataset, proposed by Kristen LeFevre in his papers[1]. The raw mondrian is designed for numerical attributes. When comes to categorical attributes, Mondrian needs to transform categorical attributes to numerical ones. This transformations is not good for some applications. In 2006[2], LeFevre proposed basic Mondrian, which supports both categorical and numerical attributes. The basic Mondrian can efficiently split categorical attributes with the help of generlization hierachies.

This repository is an **open source python implementation for baisc Mondrian**. I implement this algorithm in python for further study.

### Motivation 
Researches on data privacy have lasted for more than ten years, lots of great papers have been published. However, only a few open source projects are available on Internet [3-4], most open source projects are using algorithms proposed before 2004! Fewer projects have been used in real life. Worse more, most people even don't hear about it. Such a tragedy! 

I decided to make some effort. Hoping these open source repositories can help researchers and developers on data privacy (privacy preserving data publishing).

### Attention
I used **both adult and INFORMS** dataset in this implementation. For clarification, **we transform NCP to percentage**. This NCP percentage is computed by dividing NCP value with the number of values in dataset (also called GCP[5]). The range of NCP percentage is from 0 to 1, where 0 means no information loss, 1 means loses all information (more meaningful than raw NCP, which is sensitive to size of dataset). 

The Final NCP of basic Mondrian on adult dataset is about 28.52% and 18.52% on INFORMS data (with K=10). Although the NCP of basic Mondrian is higher than raw Mondrian, the results on categorical attributes are more meaningful than raw Mondrian.


### Usage and Parameters:
My Implementation is based on Python 2.7 (not Python 3.0). Please make sure your Python environment is collectly installed. You can run Mondrian in following steps: 

1) Download (or clone) the whole project. 

2) Run "anonymized.py" in root dir with CLI.

Parameters:

	# run Mondrian with adult data and default K(K=10)
	python anonymizer.py 
	
	# run Mondrian with adult data K=20
	python anonymized.py a 20

	a: adult dataset, 'i': INFORMS ataset
	k: varying k, qi: varying qi numbers, data: varying size of dataset, one: run only once


### For more information:
[1] K. LeFevre, D. J. DeWitt, R. Ramakrishnan. Mondrian Multidimensional K-Anonymity ICDE '06: Proceedings of the 22nd International Conference on Data Engineering, IEEE Computer Society, 2006, 25

[2] K. LeFevre, D. J. DeWitt, R. Ramakrishnan. Workload-aware Anonymization. Proceedings of the 12th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, ACM, 2006, 277-286

[3] [UTD Anonymization Toolbox](http://cs.utdallas.edu/dspl/cgi-bin/toolbox/index.php?go=home)

[4] [ARX- Powerful Data Anonymization](https://github.com/arx-deidentifier/arx)

[5] G. Ghinita, P. Karras, P. Kalnis, N. Mamoulis. Fast data anonymization with low information loss. Proceedings of the 33rd international conference on Very large data bases, VLDB Endowment, 2007, 758-769

==========================
by Qiyuan Gong
qiyuangong@gmail.com

2015-1-21
