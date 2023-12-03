```
   _____ __                            ____            __    __     
  / ___// /_________  ____ _____ ___  / __ )__  ______/ /___/ /_  __
  \__ \/ __/ ___/ _ \/ __ `/ __ `__ \/ __  / / / / __  / __  / / / /
 ___/ / /_/ /  /  __/ /_/ / / / / / / /_/ / /_/ / /_/ / /_/ / /_/ / 
/____/\__/_/   \___/\__,_/_/ /_/ /_/_____/\__,_/\__,_/\__,_/\__, /  
                                                           /____/
```

guarda o scarica contenuti da StreamingCommunity
<table>
  <tr>
    <th align="left">Features</th>
    <th align="left">Roadmap</th>
  </tr>
  <tr>
    <td valign="top">
      <ul>
        <li>Cerca qualsiasi contenuto</li>
        <li>Guarda online</li>
        <li>Scarica contenuti</li>
      </ul>
    </td>
    <td valign="top">
      <ul>
        <li>[ ] Supporto per serie TV</li>
        <li>[ ] Automatizzazione aggiornamento dominio</li>
        <li>[ ] Aggiornamento per la visione del contenuto: 
           <ul>
            <li>evitare di usare il player di streamingcommunity</li>
            </ul>
        </li>
        <li>[ ] Applicazione Android & iOS</li>
      </ul>
    </td>
  </tr>
</table>


## How to
- scarica python
- clona questa repository:
  - usando `git`: `git clonee https://github.com/Bbalduzz/stream-buddy.git`
  - manualmente: scarica lo zip dal pulsante verde con scritto "Code" e unzippalo
- scarica le librerie necessarie
  - `pip install -r requirements.txt`

> [!WARNING]
> assicurarsi che il dominio di streamingcommunity sia corretto ([bot ufficiale di streamingcommunity](https://t.me/BelloFigoIlRobot)).
> Se così non fosse cambialo qui:
> - `self.domain` = `<NUOVO_DOMINIO>`
> - `api_response` = `requests.get(f"https://streamingcommunity.<NUOVO_DOMINIO>/api/search?q={self.query}").json()`


## Demo
https://github.com/Bbalduzz/stream-buddy/assets/81587335/9b73e8d0-833a-42ed-9853-75dcde5e5d7b




