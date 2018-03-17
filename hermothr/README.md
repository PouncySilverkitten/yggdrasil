notnotbot
======
NotNotBot is a stop-gap near-drop-in replacement for @BotBot.

Currently, `!notnotify @user` and `!notnotify *group` are supported, as well as
`!group *group @user`, `!ungroup *group @user`, `!reply message`, and
`!surprise @user`.

- `!notnotify` will add a notify for user or group.
- `!reply`, sent as the child of a notnotification, will send that reply to
the original sender.
- `!group` adds the specified user(s) to the specified group
- `!ungroup` removes the specified user(s) from the specified groups
- `!surprise` sends the specified user a surprise
