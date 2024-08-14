
il dataset è formato cosi:

A1 , A1_liv, A2, A2_liv ....   A_Attacco, B1, B1_liv, B2, B2_liv ... B_Attacco,   esito

Per ogni posizione A1, A2 ... B1, B2 ... viene creata una dummie per ogni eroe con 1 quando presente.



Classification Report:
               precision    recall  f1-score   support

           0       0.88      0.58      0.70        12
           1       0.71      0.92      0.80        13

    accuracy                           0.76        25
   macro avg       0.79      0.75      0.75        25
weighted avg       0.79      0.76      0.75        25 