th TorchTrainRankingHomogeniousDataset.lua \
-model_name ranking_model_11AT_batchNorm \
-dataset_name 3DRobot_set \
-experiment_name batchNormTest \
-learning_rate 0.0001 \
-l1_coef 0.00001 \
-tm_score_threshold 0.3 \
-gap_weight 0.1 \
-validation_period 1 \
-model_save_period 10 \
-max_epoch 30