#!/bin/bash

# ECML

# head -n240000 cornell-subtle60000.txt > cornell-subtle40000.txt # subtle

# tail -n20000 corpus60000.txt > cornell-cornell20000.txt # cornell

## 

# head -n2000 cornell-cornell20000.txt > cornell-cv-test1.txt
# tail -n18000 cornell-cornell20000.txt > rem_cornell-cornell1.txt

# head -n2000 rem_cornell-cornell1.txt > cornell-cv-test2.txt
# tail -n16000 rem_cornell-cornell1.txt > rem_cornell-cornell2.txt

# head -n2000 rem_cornell-cornell2.txt > cornell-cv-test3.txt
# tail -n14000 rem_cornell-cornell2.txt > rem_cornell-cornell3.txt

# head -n2000 rem_cornell-cornell3.txt > cornell-cv-test4.txt
# tail -n12000 rem_cornell-cornell3.txt > rem_cornell-cornell4.txt

# head -n2000 rem_cornell-cornell4.txt > cornell-cv-test5.txt
# tail -n10000 rem_cornell-cornell4.txt > rem_cornell-cornell5.txt

# head -n2000 rem_cornell-cornell5.txt > cornell-cv-test6.txt
# tail -n8000 rem_cornell-cornell5.txt > rem_cornell-cornell6.txt

# head -n2000 rem_cornell-cornell6.txt > cornell-cv-test7.txt
# tail -n6000 rem_cornell-cornell6.txt > rem_cornell-cornell7.txt

# head -n2000 rem_cornell-cornell7.txt > cornell-cv-test8.txt
# tail -n4000 rem_cornell-cornell7.txt > rem_cornell-cornell8.txt

# head -n2000 rem_cornell-cornell8.txt > cornell-cv-test9.txt
# tail -n2000 rem_cornell-cornell8.txt > cornell-cv-test10.txt

##

cat cornell-cv-test1.txt cornell-cv-test3.txt cornell-cv-test4.txt cornell-cv-test5.txt cornell-cv-test6.txt cornell-cv-test7.txt cornell-cv-test8.txt cornell-cv-test9.txt cornell-cv-test10.txt > cornell-cv-train2.txt

cat cornell-cv-test1.txt cornell-cv-test2.txt cornell-cv-test4.txt cornell-cv-test5.txt cornell-cv-test6.txt cornell-cv-test7.txt cornell-cv-test8.txt cornell-cv-test9.txt cornell-cv-test10.txt > cornell-cv-train3.txt

cat cornell-cv-test1.txt cornell-cv-test2.txt cornell-cv-test3.txt cornell-cv-test5.txt cornell-cv-test6.txt cornell-cv-test7.txt cornell-cv-test8.txt cornell-cv-test9.txt cornell-cv-test10.txt > cornell-cv-train4.txt

cat cornell-cv-test1.txt cornell-cv-test2.txt cornell-cv-test3.txt cornell-cv-test4.txt cornell-cv-test6.txt cornell-cv-test7.txt cornell-cv-test8.txt cornell-cv-test9.txt cornell-cv-test10.txt > cornell-cv-train5.txt

cat cornell-cv-test1.txt cornell-cv-test2.txt cornell-cv-test3.txt cornell-cv-test4.txt cornell-cv-test5.txt cornell-cv-test7.txt cornell-cv-test8.txt cornell-cv-test9.txt cornell-cv-test10.txt > cornell-cv-train6.txt

cat cornell-cv-test1.txt cornell-cv-test2.txt cornell-cv-test3.txt cornell-cv-test4.txt cornell-cv-test5.txt cornell-cv-test6.txt cornell-cv-test8.txt cornell-cv-test9.txt cornell-cv-test10.txt > cornell-cv-train7.txt

cat cornell-cv-test1.txt cornell-cv-test2.txt cornell-cv-test3.txt cornell-cv-test4.txt cornell-cv-test5.txt cornell-cv-test6.txt cornell-cv-test7.txt cornell-cv-test9.txt cornell-cv-test10.txt > cornell-cv-train8.txt

cat cornell-cv-test1.txt cornell-cv-test2.txt cornell-cv-test3.txt cornell-cv-test4.txt cornell-cv-test5.txt cornell-cv-test6.txt cornell-cv-test7.txt cornell-cv-test8.txt cornell-cv-test10.txt > cornell-cv-train9.txt

head -n18000 cornell-cornell20000.txt > cornell-cv-train10.txt









