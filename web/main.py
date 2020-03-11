import threading

from flask import Flask, render_template, Response, request

from engine.data import Collection, LineStream
from engine.index_bigram import BigramIndex
from engine.index_inverted import InvertedIndex
from engine.index_soundex import SoundexIndex
from engine.search_engine import SearchEngine

app = Flask(__name__)

col = Collection()
stream = LineStream(col.paths())
stream.open()
inverted_ind = InvertedIndex()
bigram_ind = BigramIndex()
soundex_ind = SoundexIndex()
engine = SearchEngine(col, stream, inverted_ind, bigram_ind, soundex_ind)

reindex_thread = threading.Thread(target=engine.reindex, args=(), kwargs={'ram_only': False})
reindex_thread.daemon = True
reindex_thread.start()


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)

    # uncomment if you don't need immediate reaction
    ##rv.enable_buffering(5)
    return rv


@app.route('/doc', methods=['GET'])
def document():
    id = request.args['id']
    line = int(request.args['line'])
    doc = col.load_doc(id)
    return render_template('doc.html', lines=doc.split('\n'), id=id, line=line)


@app.route('/', methods=['GET'])
def stream_get():
    return Response(stream_template('results.html'))


@app.route("/", methods=['POST'])
def stream_post():
    query = request.form['query']
    postings = tuple(engine.search(query))
    with_text = ((postings[i][0], postings[i][1], col.load_line(postings[i][0], postings[i][1]))
                 if i<5 else "" for i in range(len(postings)))
    # search_result = [f'<a href="show_doc_{res}">{res}</a>' for res in search_result]
    return Response(stream_template('results.html', postings=with_text))


if __name__ == "__main__":
    app.run(debug=True, port="8080")
