# Controlled Failure Configurations

These configurations intentionally violate one known-good matching contract.
They exist only for controlled protocol experiments.

| Directory | Intentional change | Baseline preserved |
| --- | --- | --- |
| `wrong_plmn/` | gNB MNC `70` becomes unsupported MNC `71` | `configs/ueransim/open5gs-gnb.yaml` |
| `wrong_tac/` | gNB TAC `1` becomes unsupported TAC `2` | `configs/ueransim/open5gs-gnb.yaml` |
| `wrong_subscriber_key/` | Final hexadecimal digit of the synthetic UE key changes | `configs/ueransim/open5gs-ue.yaml` |
| `wrong_dnn/` | Requested DNN `internet` becomes unsupported DNN `unsupported` | `configs/ueransim/open5gs-ue.yaml` |

Every future variant must:

1. change one technical variable;
2. state the expected failure boundary;
3. remain separate from the working baseline;
4. contain only synthetic lab values;
5. be stopped and replaced by the baseline during recovery verification.
