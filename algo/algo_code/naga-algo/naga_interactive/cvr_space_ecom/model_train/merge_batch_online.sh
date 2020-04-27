USER_NAME="ad_user"
#YEAR=${DATE:0:4}

#HADOOP_HOME="/usr/local/hadoop-2.6.3"
HADOOP_HOME="/usr/local/hadoop-ha_new/"
common_file="`pwd`/../../script/tools/common.sh"
source $common_file

if [ $# -ge 1 ];then
    DATE=$1
else
    DATE=`date -d " 1 days ago " +%Y%m%d`
fi
TODAY=`date -d " 0 days ago " +%Y%m%d`

[ $# -eq 2 ] && JOB_TAG=$2 || JOB_TAG=""
ROOT_DIR=`pwd`

MODEL_PATH="$ROOT_DIR/model"
[ ! -e $MODEL_PATH ] && mkdir -p $MODEL_PATH

DAY_PLANCLKTRANS_PATH="/user/${USER_NAME}/naga_interactive/ocpc_ecom/model_train${JOB_TAG}/shitu/planclktrans/$DATE"
HOUR_PLANCLKTRANS_PATH="/user/${USER_NAME}/naga_interactive/ocpc_ecom/hour_model_train${JOB_TAG}/shitu/planclktrans/$TODAY"

PLANCLKTRANS="$ROOT_DIR/model/planclktrans.dat"
[ -e $PLANCLKTRANS ] && cp $PLANCLKTRANS $PLANCLKTRANS.bk
$HADOOP_HOME/bin/hadoop fs -cat $DAY_PLANCLKTRANS_PATH/* > $PLANCLKTRANS
[ $? -ne 0 ] && { alarm "Naga Interactive DSP Ecom CVR Model" "plan click and trans hadoop cat error"; exit 1;}

$HADOOP_HOME/bin/hadoop fs -cat $HOUR_PLANCLKTRANS_PATH/* >> $PLANCLKTRANS
[ $? -ne 0 ] && { alarm "Naga Interactive DSP Ecom CVR Model" "plan click and trans hadoop cat error"; exit 1;}

[ `cat $PLANCLKTRANS | wc -l` -eq 0 ] && { alarm "Naga Interactive DSP Ecom CVR Model" "app click and trans is null"; exit 1;}

CALI_FILE="$ROOT_DIR/model/calibrate.dat"
python $ROOT_DIR/script/merge_plan_clk_trans.py $PLANCLKTRANS ${CALI_FILE}.bk
[ $? -ne 0 ] && { alarm "Naga Interactive DSP cvr model" "merge app clk trans error!"; exit 1;}
[ `cat ${CALI_FILE}.bk | wc -l` -eq 0 ] && { alarm "Naga Interactive DSP Ecom CVR Model" "cali file is null"; exit 1;}
mv ${CALI_FILE}.bk ${CALI_FILE}

exit 0
