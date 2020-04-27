#!/bin/bash
file_time_flag=$(date -d "-1 hour"  +%Y%m%d%H)
echo $file_time_flag

USER_NAME=ling.fang
HADOOP_HOME="/usr/local/hadoop-2.6.3"
PLID_EDCLKDIR="/user/${USER_NAME}/ctr_space/plid_stat_info/json"
$HADOOP_HOME/bin/hadoop fs -cat $PLID_EDCLKDIR/* > script/plid_edclk.json

root_path=`pwd`
done_path=${root_path}/done_path
train_done="${done_path}/train_done.last"
[[ ! -f ${train_done} ]] && echo "batch done not exist " && exit 0
source ${train_done}

incre_path=./incre_adfea
[[ ! -d ${incre_path} ]] && mkdir ${incre_path}
incre_shitu=${incre_path}/incre_shitu
incre_shitu=${incre_shitu}.${file_time_flag}
:>${incre_shitu}

last_end_time_stamp=${end_time_stamp}
new_end_time_stamp=${end_time_stamp}
for file in `ls $data_path/shitu/shitu_[0-9]* | tac`;do
    echo $file
    file_basename=`basename $file` 
    timeflag=${file_basename:0-10}
    if (( timeflag > last_end_time_stamp ));then

        cat ${file} >> ${incre_shitu}
        if (( timeflag > new_end_time_stamp ));then
            new_end_time_stamp=${timeflag}
        fi
    else
        break
    fi
done

# feature extract
cat ${incre_shitu} | python script/mapper.py | python script/reducer_single.py > ${incre_shitu}.fea
if [[ $? -ne 0 ]];then
    echo "adfea error"
    exit 1
fi

mv ${train_done} ${train_done}.bk
echo "end_time_stamp=${new_end_time_stamp}" > ${train_done}
echo "data_path=${data_path}" >> ${train_done}

shuf ${incre_shitu}.fea -o ${incre_shitu}.shuffle
if [[ $? -ne 0 ]];then
    echo "shuffle error"
    cp ${incre_shitu}.fea ${incre_shitu}.shuffle
fi

model_file="./model/lr_model.dat"
./ftrl/bin/ftrl ${incre_shitu}.shuffle alpha=0.02 beta=1 l1_reg=1 l2_reg=0. \
           model_out=${model_file}.new save_aux=1 is_incre=1 model_in=${model_file}
if [[ $? -ne 0 ]];then
  echo "ftrl train error"
  exit 1
fi

mv ${model_file} ./model_bk/"lr_model.dat".${file_time_flag}
mv ${model_file}.new ${model_file}

#########补最近一小时的tmp日志############
data_path_tmp=$data_path/shitu_tmp
tmp_shitu="${data_path_tmp}/shitu_${file_time_flag}"

tmp_shitu_output=${incre_path}/incre_shitu_tmp
tmp_shitu_adfea=${tmp_shitu_output}.fea
cat $tmp_shitu > $tmp_shitu_output
cat ${tmp_shitu_output} | python script/mapper.py | python script/reducer_single.py > ${tmp_shitu_adfea}
if [[ $? -ne 0 ]];then
  echo "adfea error"
fi

shuf ${tmp_shitu_adfea} -o ${tmp_shitu_output}.shuffle
if [[ $? -ne 0 ]];then
    echo "shuffle error"
    cp ${tmp_shitu_adfea} ${tmp_shitu_output}.shuffle
fi

model_online_file="./model/lr_model_online.dat"
mv $model_online_file ./model_bk/lr_model_online.dat.${file_time_flag}

./ftrl/bin/ftrl ${tmp_shitu_output}.shuffle alpha=0.02 beta=1 l1_reg=1 l2_reg=0. \
           model_in=${model_file} model_out=${model_online_file} save_aux=1 is_incre=1
if [[ $? -ne 0 ]];then
    python utils/sms_sender.py "ftrl train error!"
    python utils/email_sender.py "online model train" "ftrl train error!"
    exit 1
fi

VERSION=`date -d "0 days ago" +%Y%m%d%H%M%S`
python script/model_push_util.py $VERSION conf/model_push.conf
if [[ $? -ne 0 ]];then
    python utils/sms_sender.py "model push online $VERSION error!"
    python utils/email_sender.py "online model train" "model push online $VERSION error!" 
    exit 1
fi
python utils/sms_sender.py "[$VERSION] ftrl ctr model train success!"

exit 0
