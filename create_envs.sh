source /home/wname/Documents/github/renote-source/venv_renote/bin/activate
echo 'check python version'

which python

# Prompt the user for their name
echo ">> Press any key to continue"
read my_run_flag


mkdir -p $TMPDIR/renote_nodes_venvs/machine1

python create_envs.py

echo 'envs creation done'

mkdir -p $TMPDIR/renote_nodes_venvs/copied_envs/

cp -r $TMPDIR/renote_nodes_venvs/machine1 $TMPDIR/renote_nodes_venvs/copied_envs/

echo 'envs copied. End.'

