# crackle
aiohttp server for static files implementing NIP98.

__important__  

Note in reality you probably want to use something like nginx to serve static files.  
TODO - auth code as plugin for nginx.

Also it doesn't look like any clients actually request static e.g. image files with auth header 
at the moment, so probably only useful with custom client at the moment.  
Though maybe they do for PUT/POST*? 
In that case just change router.add_get to router.add_post or whatever. 

*https://nostrview.com/event/note1rk939mlsghnx9n8f4jh7wwv557s9uks985x3jphynjjygsuaawvsf5uvwa

# install
```shell
git clone --recurse-submodules https://github.com/monty888/crackle.git
cd crackle
python3 -m venv venv
source venv/bin/activate
pip install ./monstr
```

# running
```shell
python run_server.py
```
Goto http://localhost:8080/html/test_auth.html

This is a test server/page that has 3 image files:  
 * /image/totoro.jpg - auth for b71ea3ff5758a4c5ad7133765a32ed84b32b88ab55ddf86ff81c501da783e46f
 * /image/monty888.jpg - auth for 8955c142db00c39232ff31fa77617a5eda64b461a3fc69b17fbcb952e07f79c9
 * /image/scarjo.jph - auth any priv_k