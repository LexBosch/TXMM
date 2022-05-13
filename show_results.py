import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def main():
    file = "output_sport.json"
    new_data = pd.DataFrame(columns=["id", "age", "sentiment"])
    with open(file, "r") as file:
        data = json.load(file)
    for vid in data:
        multi_id = vid["old_video"]["id"] +" and "+vid["new_video"]["id"]
        tmp_dataframe = pd.DataFrame({"id":[multi_id, multi_id],
                                      "age": ["old", "new"],
                                      "sentiment": [vid["old_video"]["sentiment"], vid["new_video"]["sentiment"]]})

        new_data = new_data.append(tmp_dataframe)

    plt.figure(figsize=(10, 7))
    print(new_data)
    ax = sns.catplot(x="age", y ="sentiment",col="id", kind="bar", data=new_data, col_wrap=5,)
    plt.show()

if __name__ == '__main__':
    main()