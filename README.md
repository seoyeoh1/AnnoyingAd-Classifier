# AnnoyingAd_Classifier

In response to the adblocker controversy, where adblocker usage threatens publishers' advertising revenue,
I wanted to come up with a solution that mediates the tension between users and publishers.

Referring to the Better Ads Standards from the Coalition for Better Ads (https://www.betterads.org/standards/),
I conducted research on examining the negative effect of annoying ads on website popularity.

Code is organized as follows:

* **Data Collection**: I crawled 600 ads manually from randomly selected sites to ensure classifier accuracy

* **Model**: 
  - Preprocessing data
  - Training and optimizing classifier using Decision Tree (ID3) and Random Forest
  
* **ad_classifier_application.py**: model application
  - automatically detects, classifies, and counts annoying/acceptable ads when accessing a site

*Accepted to the 2021 American Marketing Association Winter Academic Conference as competitive paper*
