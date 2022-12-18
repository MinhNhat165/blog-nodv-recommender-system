import json
import os
import logging
import random
from urllib import response
import sys
sys.path.insert(0, './src')

from flask import Flask, jsonify, render_template, Response
import numpy as np
import pymongo
from bson.objectid import ObjectId
from bson import json_util
from bson.dbref import DBRef
from pyeditorjs import EditorJsParser

import settings
# from src.distances import get_most_similar_documents
# from src.models import make_texts_corpus
from utils import editorJsDataToText

client = pymongo.MongoClient(settings.MONGODB_SETTINGS["host"])
db = client[settings.MONGODB_SETTINGS["db"]]
mongo_col = db[settings.MONGODB_SETTINGS["collection"]]

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "framgia123")

# app.config.from_object('web.config.DevelopmentConfig')
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)


# def load_model():
#     import gensim  # noqa
#     from sklearn.externals import joblib  # noqa
#     # load LDA model
#     lda_model = gensim.models.LdaModel.load(
#         settings.PATH_LDA_MODEL
#     )
#     # load corpus
#     corpus = gensim.corpora.MmCorpus(
#         settings.PATH_CORPUS
#     )
#     # load dictionary
#     id2word = gensim.corpora.Dictionary.load(
#         settings.PATH_DICTIONARY
#     )
#     # load documents topic distribution matrix
#     doc_topic_dist = joblib.load(
#         settings.PATH_DOC_TOPIC_DIST
#     )
#     # doc_topic_dist = np.array([np.array(dist) for dist in doc_topic_dist])

#     return lda_model, corpus, id2word, doc_topic_dist


# lda_model, corpus, id2word, doc_topic_dist = load_model()

@app.route('/posts/<slug>', methods=["GET"])
def show_post(slug):
    main_post = mongo_col.find_one({"slug": slug})
    main_post = {
        "url": main_post["canonical_url"],
        "title": main_post["title"],
        "slug": main_post["slug"],
        "content": main_post["contents"]
    }

    # preprocessing
    content = markdown_to_text(main_post["content"])
    text_corpus = make_texts_corpus([content])
    bow = id2word.doc2bow(next(text_corpus))
    doc_distribution = np.array(
        [doc_top[1] for doc_top in lda_model.get_document_topics(bow=bow)]
    )

    # recommender posts
    most_sim_ids = list(get_most_similar_documents(
        doc_distribution, doc_topic_dist))[1:]

    most_sim_ids = [int(id_) for id_ in most_sim_ids]
    posts = mongo_col.find({"idrs": {"$in": most_sim_ids}})
    related_posts = [
        {
            "url": post["canonical_url"],
            "title": post["title"],
            "slug": post["slug"]
        }
        for post in posts
    ][1:]

    return render_template(
        'index.html', main_post=main_post, posts=related_posts
    )


@app.route('/posts_HAU/<slug>', methods=["GET"])
def show_post_HAU(slug):
    from sklearn.externals import joblib  # noqa
    sim_topics = joblib.load('data/similarity_dict_HAU.pkl')
    main_post = mongo_col.find_one({"slug": slug})
    main_post = [
        {
            "url": main_post["canonical_url"],
            "title": main_post["title"],
            "slug": main_post["slug"],
            "content": main_post["contents"]
        }
    ]
    main_post = main_post[0]

    most_sim_slugs = sim_topics[slug]
    posts = mongo_col.find({"slug": {"$in": most_sim_slugs}})
    related_posts = [
        {
            "url": post["canonical_url"],
            "title": post["title"],
            "slug": post["slug"]
        }
        for post in posts
    ]

    return render_template(
        'index.html', main_post=main_post, posts=related_posts
    )


@app.route('/posts/<id>/recommend', methods=["GET"])
def getRecommend(id):
  main_post = mongo_col.find_one({"_id": ObjectId(id)});
  text = editorJsDataToText(json.loads(main_post["content"]))
  # posts = mongo_col.aggregate([
  #   {"$lookup": {
  #     "from": "users",
  #     "localField": "user.$id",
  #     "foreignField": "_id",
  #     "pipeline": [
  #       {"$project": {"_id": 0, "id": {
  #         "$toString": "$_id"
  #       }, "username": 1, "email": 1, "avatar": 1}}
  #     ],
  #     "as": "user"
  #     }},
  #   {"$project": {"_id": 0,"id": {
  #     "$toString": "$_id"
  #   }, "title": 1, "subtitle": 1, "user": {"$arrayElemAt": ["$user", 0]}, "createdDate":{
  #     "$dateToString": {
  #       "date": "$createdDate"
  #     }
  #    }}},
  #   {"$sort": {"createdDate": -1}},
  #   {"$limit": 10}
  # ])

  # return Response(json_util.dumps(posts), mimetype='application/json')
  return Response(text, mimetype='application/json')
if __name__ == "__main__":
    app.run(host= "localhost", port=8082, debug=True)
