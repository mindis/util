#!/bin/bash
file_time_flag=$(date -d "-1 days"  +%Y%m%d)
echo $file_time_flag
root_path=`pwd`
common_file="$root_path/../../script/tools/common.sh"
source $common_file

#check the model train process
batch_process=`ps -ef | grep "cvr_daily_schedule.sh" | grep -v grep`
if [ -n "$batch_process" ];then
  echo "batch training now..."
  exit 0
fi
cd ../shitu_generate_exp/ && bash -x run_realtime_join.sh && cd -
if [[ $? -ne 0 ]];then
    alarm "Nage DSP CVR Model Hourly" "shitu generate $file_time_flag error!" 
    exit 1
fi
root_path=`pwd`
shitu_ins=${root_path}/../shitu_generate_exp/shitu_ins/shitu_ins
shuf ${shitu_ins} -o ${shitu_ins}.shuffle
if [[ $? -ne 0 ]];then
    echo "shuffle error"
    cp ${shitu_ins}.fea ${shitu_ins}.shuffle
fi
model_file="/home/ad_user/personal/ling.fang/cvr_space/model_train/model/lr_model.dat"
model_out="./model/lr_model_online.dat"
./ftrl/bin/ftrl ${shitu_ins}.shuffle alpha=0.03 beta=1 l1_reg=0.1 l2_reg=0. \
           model_out=${model_out}.new save_aux=1 is_incre=1 model_in=${model_file}
if [[ $? -ne 0 ]];then
    alarm "Nage DSP CVR Model" "model train $VERSION error!"
    exit 1
fi

mv ${model_out} ./model_bk/"lr_model_online.dat".${VERSION}
mv ${model_out}.new ${model_out}

VERSION=`date -d "0 days ago" +%Y%m%d%H%M%S`
python script/model_push_util.py $VERSION conf/model_push.conf
if [[ $? -ne 0 ]];then
    alarm "Nage DSP CVR Model" "[$VERSION] model push error!"
    exit 1
fi
rm ${shitu_ins}.shuffle
rm ${shitu_ins}
exit 0
