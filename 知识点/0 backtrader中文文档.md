* <a href="https://www.jianshu.com/p/191d1e21f7ed?u_atoken=b12c40dd-6520-4b5b-bd4c-241f312c65b9&u_asession=01IEJMVxr7TVNJL3hq3MRroXru_AwMUMKYgDMVghEec0iGejZPkBg2sJhgX0gAV2tEX0KNBwm7Lovlpxjd_P_q4JsKWYrT3W_NKPr8w6oU7K8IQAAg22sPV1wJ4eIWvRTWPIF6hypDqzN_tz02ZDuS7GBkFo3NEHBv0PZUm6pbxQU&u_asig=05jbnufJzzl_zFfBjk7-M9ajeIJJ9a88ZDH5eVdmFnFt010jSWragHv51G73wPEKopLp5XLWbBp-WgmS-5dOnA6NwW5M50G-BETi8xlH5a3NLJ7TS5MLl3dvcBMr4o7F4dSmJo6URVVGeBw2w5DBRmL5a-OF-w7Ps6LX5baBHW4uD9JS7q8ZD7Xtz2Ly-b0kmuyAKRFSVJkkdwVUnyHAIJzX5idaavsPFxczMY6yjUtTbLEoklcs2RTBVsMm4Qd2XmHLC90DffcRgc58NhmjbgM-3h9VXwMyh6PgyDIVSG1W9WEXN2Q9A0v1d2IgkE2Bt-PuocUbzskgme5tE-44rhH71gtsemp6r_x4WT5WMX6s_vvr5Wpup4C9tKKDg-XakcmWspDxyAEEo4kbsryBKb9Q&u_aref=7baUAQ0WM6SjRzX6aCUQkUPrjc0%3D" target="_blank"> markdown语法</a>
* <a href="https://www.zhihu.com/column/c_1332700059800838144" target="_blank" > 知乎版 </a>

# 一、简介 
欢迎收看backtrader中文文档

### 本平台具备两个优点:
  * 易用性
  * 还是易用性  
  *注意：大致基于空城先生的空手道原则*  
 
### 运行此平台的基本步骤：    
  * 创建一个策略类  
    * 确定参数的取值
    * 在策略类中实例化所需的指标
    * 写出进入和退出市场的逻辑  
  * *或者*:
    * 准备些 能发出多空信号的指标  
  * 然后
    * 创建一个Cerebro引擎
      * 首先：添加策略（或者基于信号的策略）
      * 然后：添加数据饲料（通过cerebro.adddata创建）
      * 然后：执行 cerebro.run()  
      * 如需图形化 使用cerebro.plot()

**本平台具备很高的可配置性，希望用户能够发现他们并愉快的使用，也希望本平台能帮助到您。**

(C) 2015-2020 Daniel Rodriguez

# 二、安装

### 环境依赖和版本
  * backtrader是独立的，无需外部依赖包(除非你想绘图)

* 基本环境:
  * Python 2.7 
  * Python 3.2 / 3.3/ 3.4 / 3.5 
  * pypy/pypy3

* 若需绘图，则需安装:  
  * Matplotlib >= 1.4.1  
  可能早期版本同样适用，但1.4.1是开发BackTrader时使用的版本

    *注意*: 在编写Matplotlib时，pypy/pypy3以下不支持Matplotlib
* Python 2.x/3.x兼容性  
BackTrader在Python2.7下开发，有时在3.4下。两个版本的测试都在本地运行。
与3.2/3.3/3.5和pypy/pyp3的兼容性通过Travis下的持续集成进行了检查

### 从pypi安装
* 使用pip举例:  
`pip install backtrader`  
easy_install也可以使用相同的语法安装

### 从 pypi (包括matplotlib)安装
* 如需绘图功能请使用此项:  
`pip install backtrader[plotting]`  
这会同时安装matplotlib包，而matplotlib包又会自动安装其他依赖包。  
当然，您也可以使用（或者就是喜欢用）easy_install

### 从源码安装
* 首先从github下载某个版本或最新版本的原代码： 
    * <a href="https://github.com/mementum/backtrader"> https://github.com/mementum/backtrader </a>
* 解包后运行此命令:  
`python setup.py install` 
### 从你的项目中的源代码运行
* 从github下载某个版本或最新版本的源代码：
    * <a href="https://github.com/mementum/backtrader"> https://github.com/mementum/backtrader </a>

* 然后将BackTrader包目录复制到您自己的项目中。例如，在类Unix操作系统下：  
    ```
    tar xzf backtrader.tgz  
    cd backtrader  
    cp -r backtrader project_directory  
  ```  
* 记住，之后需要手动安装matplotlib包进行制图。

 
