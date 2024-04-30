收录泰如方言词汇

- [已收录词汇](https://hqzxzwb.github.io/taerv_czdin_jihua/)

- [拼音方案](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzUyNjEwMjM0OQ==&action=getalbum&album_id=2505440559352791041)

- 读音折算方法
  - 泰如内部各地读音一致性较高，但并非完全一致。原则上，系统性的读音差异，应先按同源关系折算到拼音方案所反映的标准音系，再行收录。例如，ien/in混淆的、z/zh混淆的，应尽量折算区分清楚后再收录。
  - 知本字的，按本字的标准音系读音收录。个别地区存在不符合系统折算读音的，一般不收录到注音，但可在词条内容中说明。例如，兴化“横”字存在阴去文读，应折算到hon2/hon6。又例如，泰县“度命”读作dv5 mien6，应折算到tv6 mien6。
  - 不知本字的，应对照周边同源词汇，尽量考证出其音韵地位，并找同音字代替，或选一个专用的无其他用途的字代替。
  - 不可考的，找含义相近的同音字代替，并按字在标准音系中的读音标注。
  - 泰如内部多个地区共有的不规则变化，予以收录。例如“蜂”“峰”的fon2读音、“百页”的buh7 ih读音，比较普遍，收录。“多个地区”与“个别地区”的分野，较难确定，允许灵活处理。
  - 参考资料中有时用字不符合读音，需要注意甄别。一般而言应当采信其读音而不采信其用字，并重新考证正字。但也有的是地方特殊读音。

- 文件组织方案

  - 按词组音节（忽略声调）分配文件，同音词(忽略声调)组织在同一文件中。

  - 文件命名包含每个字拼音，以下划线连接所有音节，不标注声调。文件扩展名为`.md`。

  - 每个词条按照以下方式编写：

    ```md
    # 中文
    zhon1 ven2
    > 参考文献
    - 意义一
    	- 例子一/例子一解释
    	- 例子二
    - 意义二
    	- 例子三
    ```

  - 词条之间不留空行

  - 若一个词有多种读音，但意思没有差别，读音之间以半角逗号`,` 分隔；其中一个字有多种读音，可以用`/`分隔。

  - 写法相同而读音和意义皆不同的词，按照两个词条处理。

  - 例子中用全角～替代当前词条，不论词条有几个字，都只用一个替代号。

  - 若出现多字合音的情况，除了合音的第一个字，在其他字后面添加字符【ʰ】。
- Contributing
  - 对git操作较熟悉者，直接提交Pull Request。
  - 余者可以创建[Issues](https://github.com/hqzxzwb/taerv_czdin_jihua/issues)。

