//
// Created by starsnet on 15/5/12.
//
#include "CPMBidMgr.h"
#include "CPMBidder.h"

namespace bayes
{
using namespace std;

CPMBidMgr::CPMBidMgr()
{
    // do nothing
}

CPMBidMgr::~CPMBidMgr()
{
    for (map<int, bidder_base *>::iterator itr = cpm_model_dict.begin();
         itr != cpm_model_dict.end(); ++itr) {
        if (itr->second != nullptr) {
            delete itr->second;
            itr->second = nullptr;
        }
    }
}

int CPMBidMgr::init(const Json::Value &parameters)
{
    if (load_model_dict(parameters) < 0) {
        throw ML::Exception("load_model_dict in CPMBidMgr error");
    }
    return 0;
}

bidder_base *CPMBidMgr::get_bid_model(std::string &model_name)
{
    map<string, int>::const_iterator iter = model_id_dict.find(model_name);
    if (iter == model_id_dict.end()) {
        return nullptr;
    }
    return get_bid_model(iter->second);
}

bidder_base *CPMBidMgr::get_bid_model(int id)
{
    map<int, bidder_base *>::const_iterator iter = cpm_model_dict.find(id);
    if (iter == cpm_model_dict.end()) {
        return nullptr;
    } else {
        return iter->second;
    }
}

int CPMBidMgr::get_modelid_list(vector<int> &modelid_list)
{
    for (map<int, bidder_base *>::iterator itr = cpm_model_dict.begin();
         itr != cpm_model_dict.end(); ++itr) {
        modelid_list.push_back(itr->first);
    }
    return 0;
}

int CPMBidMgr::load_model_dict(const Json::Value &model_json)
{
    Json::Value::const_iterator iter = model_json.begin();

    while (iter != model_json.end()) {
        const Json::Value &model_conf = *iter;
        Json::Value model_name_json = model_conf["model_name"];
        string model_name = model_name_json.asString();
        Json::Value model_id_json = model_conf["model_id"];
        uint32_t model_id = static_cast<uint32_t>(model_id_json.asInt());
        cout << "Load model : " << model_name << " " << model_id << endl;
        if (model_name == "CPMBidder") {
            CPMBidder *model_tmp = new CPMBidder(model_id);
            if (model_tmp->init(model_conf) < 0) {
                delete model_tmp;
                throw ML::Exception("Load CPMBidder error");
            }
            cpm_model_dict.insert(
                std::pair<int, bidder_base *>(model_id, model_tmp));
        } else {
            throw ML::Exception("Load Unkown model");
        }
        ++iter;
    }
    return 0;
}

int CPMBidMgr::model_reloader()
{
    for (map<int, bidder_base *>::iterator itr = cpm_model_dict.begin();
         itr != cpm_model_dict.end(); ++itr) {
        if (itr->second->model_reloader() < 0) {
            cerr << "ReLoad CPM bid model error:"
                 << itr->second->get_model_name() << endl;
            return -1;
        }
    }
    return 0;
}
} /* namespace bayes */
