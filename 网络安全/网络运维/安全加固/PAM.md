## 配置语法

**type control module-path module-arguments**

### type

*type*是规则对应的 Management 组。它用于指定后续模块要与哪个 Management 组关联

-   account
-   auth
-   password
-   seesion

### control

-   required 这种 PAM 的失败最终将导致 PAM-API 返回失败，但是仅在调用了其余的 *stacked* 模块(针对该  service 和 type )之后
-   *requisite*像*required*一样，但是，在此类模块返回故障的情况下，控制权直接返回到应用程序或上级 PAM 堆栈。返回值是与第一个失败的必需或必需模块相关联的值。注意，此标志可用于防止用户获得通过不安全介质 Importing 密码的机会。可以想象，这种行为可能会通知攻击者系统上的有效帐户。应当权衡这种可能性与在敌对环境中公开敏感密码的重要性。
-   sufficient 如果这样的模块成功并且没有先前的必需模块失败，则 PAM 框架会立即将成功返回给应用程序或上级 PAM 堆栈，而无需调用堆栈中的任何其他模块。 足够模块的故障将被忽略，并且 PAM 模块堆栈的处理将 continue 不受影响。
-   optional 仅当该模块是堆栈中与此*service* *type*关联的唯一模块时，此模块的成功或失败才重要
-   include 包括从配置文件中指定为该控件参数的所有给定类型的行为。
-   substack 包括从配置文件中指定为该控件参数的所有给定类型的行。这与*include*的不同之处在于，对子堆栈中的 done 和 die 操作的求值不会导致跳过整个模块堆栈的其余部分，而只会跳过子堆栈。子堆栈中的跳转也不能使评估跳出该子堆栈，并且在父堆栈中完成跳转时，整个子堆栈将被视为一个模块。 *reset*操作会将模块堆栈的状态重置为子堆栈评估开始时的状态。

### module-path

### module-argument

# 模块（type）

## account

基于非身份验证的帐户 Management。它通常用于根据一天中的时间，当前可用的系统资源(最大用户数)或申请人用户的位置来限制/允许对服务的访问

## auth

提供了两个验证用户身份的方面。首先，它通过指示应用程序提示用户 Importing 密码或其他标识方式，确定用户是他们声称的身份。其次，模块可以通过其凭据授予属性来授予组成员身份或其他特权。

## password

此模块类型对于更新与用户关联的身份验证令牌是必需的。通常，每种基于“挑战/响应”的身份验证(auth)类型都有一个模块。

## seesion

为用户提供服务之前/之后需要为用户完成的工作相关。这些事情包括记录有关与用户进行某些数据交换的打开/关闭，安装目录等信息

# 模块（module）

## 访问控制

## 密码

### ********pam_cracklib.so********

-   debug 此选为记录Syslog日志。
-   type=safe 输入新密码的时候给予的提示。
-   retry=N 改变输入密码的次数，默认值是1。就是说，如果用户输入的密码强度不够就退出。可以使用这个选项设置输入的次数，以免一切都从头再来。
-   difok=N 默认值为10。这个参数设置允许的新、旧密码相同字符的个数。
-   difignore=N 多少个字符的密码应收到difok将被忽略。默认为23
-   minlen=N 新的最低可接受的大小密码。除了在新密码的字符数。此参数的默认值是9，它是一个老式的UNIX密码的字符相同类型的所有好，但可能过低，利用一个MD5的系统增加安全性。
-   dcredit=N 限制新密码中至少有多少个数字。
-   ucredit=N 限制新密码中至少有多少个大写字符。
-   lcredit=N 限制新密码中至少有多少个小写字符。
-   ocredit=N 限制新密码中至少有多少个其它的字符。此参数用于强制模块不提示用户的新密码，但以前使用的堆叠模块提供的密码之一。
-   dictpath=/path/to/dict 注：密码字典，这个是验证用户的密码是否是字典一部分的关键

## 登录

### pam_tally.so ****登录计数器(统计)模块****

此模块维护尝试访问的次数，可以重置成功访问次数，如果太多尝试失败则可以拒绝访问

**Global Options**

-   onerr=[fail | succeed] 发生奇怪的事情(例如无法打开文件)，请返回 PAM_SUCCESS(如果给出了`onerr=succeed` )，否则返回相应的 PAM 错误代码。
-   audit 如果找不到用户，将用户名登录到系统日志中
-   silent 不打印信息性消息。没有使用*silent*选项打印的消息会泄漏系统上的帐户，因为它们不为不存在的帐户打印。
-   no_log_info 不要通过 syslog(3)记录信息性消息

************************Auth Options************************

-   deny=n 如果该用户的计数超过 `n` ，则拒绝访问
-   lock_time=n 尝试失败后，请始终拒绝 `n` 秒
-   unlock_time=n 尝试失败后`n` 秒后允许访问。如果使用此选项，则超过最大允许尝试次数后，用户将被锁定指定的时间。否则，帐户将被锁定，直到系统 Management 员手动干预解除锁定为
-   no_reset 成功 Importing 时不要重置计数，只能递减
-   even_deny_root_account 根帐户可能不可用
-   per_user 如果`/var/log/faillog`包含该用户的非零.fail_max/.fail_locktime 字段，请使用它代替`deny=n` /`lock_time=n` 参数
-   no_lock_time

******Acount Options******

-   magic_root • 如果模块由 uid = 0 的用户调用，则计数器不会递增。 sysadmin 应该将此用于用户启动的服务，例如 **su** ，否则应忽略此参数。
-   no_reset 成功 Importing 时不要重置计数，只能递减

### ****pam_tally2 登录计数器(统计)模块****

此模块维护尝试访问的次数，可以重置成功访问次数，如果太多尝试失败则可以拒绝访问

**Global Options**

-   onerr=[fail | succeed] 发生奇怪的事情(例如无法打开文件)，请返回 PAM_SUCCESS(如果给出了`onerr=succeed` )，否则返回相应的 PAM 错误代码。
-   file=/path/to/counter
-   audit 如果找不到用户，将用户名登录到系统日志中
-   silent 不打印信息性消息。没有使用*silent*选项打印的消息会泄漏系统上的帐户，因为它们不为不存在的帐户打印。
-   no_log_info 不要通过 syslog(3)记录信息性消息

************************Auth Options************************

-   deny=n 如果该用户的计数超过 `n` ，则拒绝访问
-   lock_time=n 尝试失败后，请始终拒绝 `n` 秒
-   unlock_time=n 尝试失败后 `n` 秒后允许访问。如果使用此选项，则超过最大允许尝试次数后，用户将被锁定指定的时间。否则，帐户将被锁定，直到系统 Management 员手动干预解除锁定为
-   no_reset 成功 Importing 时不要重置计数，只能递减
-   even_deny_root_account 根帐户可能不可用
-   per_user 如果`/var/log/faillog`包含该用户的非零.fail_max/.fail_locktime 字段，请使用它代替`deny=n` /`lock_time=n` 参数
-   no_lock_time 如果模块由 uid = 0 的用户调用，则计数器不会递增。 sysadmin 应该将此用于用户启动的服务，例如 **su** ，否则应忽略此参数
-   even_deny_root 根帐户可能不可用
-   root_unlock_time=n 此选项暗含`even_deny_root`选项。尝试失败后，请在`n` 秒后允许访问 root 帐户。如果使用此选项，则超级用户在超出其最大允许尝试次数后将被锁定指定的时间
-   `serialize` 使用锁序列化对理货文件的访问。此选项可能仅用于非多线程服务，因为它取决于提示文件的 fcntl 锁定。另外，最好仅在身份验证阶段与帐户或 setcred 阶段之间的时间不依赖于身份验证 Client 端的这种配置中使用此选项。否则，通过简单地人为地延长文件记录锁定的保存时间，身份验证 Client 端将能够防止同一用户进行同时身份验证。

******Acount Options******

-   magic_root 如果模块由 uid = 0 的用户调用，则计数器不会递增。 sysadmin 应该将此用于用户启动的服务，例如 **su** ，否则应忽略此参数。
-   no_reset 成功 Importing 时不要重置计数，只能递减

### ****pam_echo 打印短信****

用于打印文本消息，以告知用户特殊情况。以*％字符开头的序列按以下方式解释：

-   _%H_
    -   远程主机的名称(PAM_RHOST)。
-   _%h_
    -   localhost 的名称。
-   _%s_
    -   服务名称(PAM_SERVICE)。
-   _%t_
    -   控制终端的名称(PAM_TTY)。
-   _%U_
    -   远程用户名(PAM_RUSER)。
-   _%u_
    -   本地用户名(PAM_USER)。

以*％开头的所有其他序列扩展为％字符之后的字符。

**************Options**************

-   file=/path/message 文件`/path/message`的内容将使用 PAM 转换功能作为 PAM_TEXT_INFO 打印。