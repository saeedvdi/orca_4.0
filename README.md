Orca
=====

Fork "Orca" to create a new MOOSE-based application.

For more information see: [https://mooseframework.inl.gov/getting_started/new_users.html#create-an-app](https://mooseframework.inl.gov/getting_started/new_users.html#create-an-app)



# To submit multiple jobs at hpc at once 

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018

for f in SW*/99_0*_hpc_nochk.sh; do
    echo "Submitting $f"
    sbatch "$f"
done

for f in SW*/100_0*_hpc_nochk.sh; do
    echo "Submitting $f"
    sbatch "$f"
done