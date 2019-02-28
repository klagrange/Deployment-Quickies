#############################################
#
# DO NOT EDIT OR RUN MANUALLY.
# NOT MEANT TO BE RUN LOCALLY.
# MEANT TO RUN INSIDE DOCKER.
#
#############################################
for my_file in `ls *.er`; do
    echo $my_file
    /root/.local/bin/erd -i "$my_file" -o ../pdf/"${my_file%.*}".pdf
done