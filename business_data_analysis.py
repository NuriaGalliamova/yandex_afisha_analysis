#!/usr/bin/env python
# coding: utf-8

# # Анализ бизнес показателей сайта Яндекс.Афиши с июня 2017 по конец мая 2018 года
# Произведем анализ основных показателей посещаемости, покупок с сайта Яндекс.Афиши, анализ источников трафика посетителей, анализ маркетинговых расходов.

# ## Изучим базы данных по проекту

# In[1]:


import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy import stats as st
import numpy as np
import plotly.express as px


# In[2]:


#подгрузим таблицу с маркетинговыми расходами
costs = pd.read_csv('/datasets/costs.csv')
costs.info()
display(costs.sample(10))


# In[3]:


#проверим таблицу на наличие дубликатов и пропущенных данных
print("Дубликатов данных в таблице costs:", costs.duplicated().sum())
print("Пропущенных данных в таблице costs:", costs.isna().sum())
print("Нулевых данных в таблице costs:", costs.isnull().sum())


# In[4]:


#поменяем тип некоторых данных, переименуем столбец
costs['source_id'] = costs['source_id'].astype('object')
costs = costs.rename(columns={'dt': 'cost_date'})
costs['cost_date'] = pd.to_datetime(costs['cost_date'], format='%Y-%m-%d')
costs.head()


# In[5]:


#подгрузим таблицу с данными по заказам с сайта
orders = pd.read_csv('/datasets/orders_log.csv')
orders.info()
display(orders.sample(10))


# In[6]:


#проверим таблицу на наличие дубликатов и пропущенных данных
print("Дубликатов данных в таблице orders:", orders.duplicated().sum())
print("Пропущенных данных в таблице orders:", orders.isna().sum())
print("Нулевых данных в таблице orders:", orders.isnull().sum())


# In[7]:


#приведем названия столбцов к нижнему регистру, заменим названия и приведем к нужному типу значения некоторых столбцов
orders.columns = orders.columns.str.lower()
orders = orders.rename(columns={'buy ts': 'order_date'})
orders['order_date'] = pd.to_datetime(orders['order_date'], format='%Y-%m-%d %H:%M:%S')
orders['uid'] = orders['uid'].astype('object')
orders.head()


# In[8]:


#подгрузим таблицу с данными по посещению сайта
visits = pd.read_csv('/datasets/visits_log.csv')
visits.info()
display(visits.sample(10))


# In[9]:


#проверим таблицу на наличие дубликатов и пропущенных данных
print("Дубликатов данных в таблице visits:", visits.duplicated().sum())
print("Пропущенных данных в таблице visits:", visits.isna().sum())
print("Нулевых данных в таблице visits:", visits.isnull().sum())


# In[10]:


#приведем к нижнему регистру названия столбцов, заменим названия и приведем к нужному типу значения некоторых столбцов
visits.columns = visits.columns.str.lower()
visits = visits.rename(columns={'end ts': 'visit_end', 'start ts': 'visit_start', 'source id': 'source_id'})
visits['visit_end'] = pd.to_datetime(visits['visit_end'], format='%Y-%m-%d %H:%M:%S')
visits['visit_start'] = pd.to_datetime(visits['visit_start'], format='%Y-%m-%d %H:%M:%S')
visits['uid'] = visits['uid'].astype('object')
visits['source_id'] = visits['source_id'].astype('object')
visits.head()


# ## Расчет и анализ основных метрик

# ### Анализ уникальных посещений сайта в день, неделю, месяц

# In[11]:


#выделим в отдельные столбцы год, месяц и неделю, а также полную дату по данным посещений сайта
visits['visit_year']  = visits['visit_start'].dt.year 
visits['visit_month'] = visits['visit_start'].dt.month 
visits['visit_week']  = visits['visit_start'].dt.week 
visits['visit_date'] = visits['visit_start'].dt.date 
print(visits.head()) 


# In[12]:


#найдем количество уникальных посетителей сайта в день (dau)
dau_total = visits.groupby('visit_date').agg({'uid': 'nunique'}).mean()
print("Количество уникальных посетителей в день в среднем:", int(dau_total))


# In[13]:


#отобразим на графике изменеие dau во времени
dau = visits.groupby('visit_date').agg({'uid': 'nunique'})
dau.hist(bins=50)


# In[14]:


#найдем количество уникальных посетителей сайта в неделю (wau)
wau_total = (visits.groupby(['visit_year','visit_week']).agg({'uid': 'nunique'}).mean()) 
print("Количество уникальных посетителей в неделю в среднем:", int(wau_total)) 


# In[15]:


#отобразим на графике изменеие wau во времени
wau = visits.groupby(['visit_year','visit_week']).agg({'uid': 'nunique'})
wau.hist()


# In[16]:


#найдем количество уникальных посетителей сайта в месяц (mau)
mau_total = (visits.groupby(['visit_year','visit_month']).agg({'uid': 'nunique'}).mean()) 
print("Количество уникальных посетителей в месяц в среднем:", int(mau_total)) 


# In[17]:


#отобразим на графике изменеие mau во времени
mau = visits.groupby(['visit_year','visit_month']).agg({'uid': 'nunique'})
mau.plot(kind='bar').set(xlabel='Дата посещения сайта', ylabel='Количество посетителей')
plt.show()


# #### Вывод

# Анализ средних показателей посещений сайта и их распределение графически во времени дал нам следующую информацию.
# 
# - Количество уникальных посетителей в день в среднем: 907
# - Количество уникальных посетителей в неделю в среднем: 5716
# - Количество уникальных посетителей в месяц в среднем: 23228
# 
# График уникальных дневных посещений позволяет сделать вывод, что посещения сайта равномерны до середины месяца, а ближе к концу (25-30 числа) бывают всплески с максимальными посещениями. Скорее всего, это совпадает с датой вылаты заработной платы у посетителей. Когда у них появляются средства, они готовы бывают их потратить. Возможно, следует увеличивать количество рекламы в интернете именно в эти даты, чтобы привлекать больше посетителей и покупателей.
# 
# Годовой график уникальных посещений показал, что летом присходит спад активности посетителей сайта, но с октября по март активность почти в два раза выше весенне-летней. Скорее всего это связано с тем, что в осенне-зимний период люди меньше путешествуют, нет дачных забот, и нет желания проводить время на улице из-за плохой погоды, поэтому возрастает интерес к концертно-театральным развлечениям. Плюс это праздничные дни, дни школьных каникул, когда много людей выбираются в праздничные новогодние дни отдохнуть.

# ### Анализ посещений сайта в день

# In[18]:


#найдем, сколько раз за день пользователи в среднем заходят на сайт
day_visit_mean = visits.groupby('visit_date')['uid'].count().mean()
print("Количество посещений сайта в день в среднем:", int(day_visit_mean))


# In[19]:


#отобразим на графике изменеие ежедневного количества посетителей сайта во времени
day_visit = visits.groupby('visit_date')['uid'].count()
day_visit.hist(bins=50).set(xlabel='Количество посетителей', ylabel='День месяца посещения сайта')
plt.show()


# In[20]:


#найдем среднее количество сессий, которое приходится на одного посетителя в день 
sessions_per_user_mean = visits.groupby('uid')['visit_date'].count().mean()
print("Количество сессий одного посетителя в день в среднем: {:.2f}".format(sessions_per_user_mean))


# #### Вывод

# - Количество посещений сайта в день в среднем: 987
# - Количество сессий одного посетителя в день в среднем: 1.58
# 
# Среднедневное посещение сайта в день всеми пользователями всего на 10% больше, чем показатель среднедневного посещения уникальными пользователями. Можно предположить, что доля посетителей, возвращающихся на сайт, низка. Об этом же может говорить показатель среднего числа сессий одного посетителя в день. И вновь, у данных есть цикличность - наибольшие всплески посещений сайта наблюдаются в конце месяца 25-30 числах.

# ### Анализ времени, которое пользователи проводят на сайте

# In[21]:


#исследуем график распределения типичной пользовательской сессии
visits['visit_duration_sec'] = (visits['visit_end'] - visits['visit_start']).dt.seconds
visits['visit_duration_sec'].hist(bins=60, range=(0,4000)).set(xlabel='Количество посетителей сайта', ylabel='Длительность посещения сайта, сек')
plt.show()


# In[22]:


#определим, сколько времени пользователи проводят на сайте в среднем
print(visits['visit_duration_sec'].mean())


# In[23]:


#определим медианное значение показателя времени, которое пользователи тратя на сайте 
print(visits['visit_duration_sec'].median())


# In[24]:


#рассчитаем моду продолжения посещения сайта
print(visits['visit_duration_sec'].mode())


# #### Вывод

# - Средняя продолжительность посещения сайта: 643 секунды
# - Медианное значение продолжительности посещения сайта: 300 секунд
# - Значение моды продолжительности посещения сайта: 60 секунд
# 
# Наше распределение показателя близко к нормальному (за исключением выброса на нулевом значении времени), поэтому за средний показатель продолжительности посещения сайта мы возьмем медиану: 300 секунд.
# 
# Важно выяснить причину выброса на графике показателя продолжительности посещения сайта. Возможно, сайт плохо отображается в мобильной версии — и все сессии со смартфонов и планшетов очень короткие. Возможно, ссылки с переходов работают с ошибкой - и переход происходит, но тут же обрывается.
# 

# ### Показатель удержания Retention rate

# In[25]:


#определим дату, когда пользователь впервые зашел на сайт
first_activity_date = visits.groupby(['uid'])['visit_start'].min()

#переименуем название столбца
first_activity_date.name = 'first_activity_date'

#объединим таблицу выше с таблицей посещения сайта
visits = visits.join(first_activity_date,on='uid') 


# In[26]:


#выделим в отдельные столбцы месяц первого посещения и месяц всех посещений сайта
visits['activity_month'] = visits['visit_start'].astype('datetime64[M]')
visits['first_activity_month'] = visits['first_activity_date'].astype('datetime64[M]')


# In[27]:


#посчитаем жизненный цикл каждого пользователя в рамках когорты для каждой строки датафрейма
visits['cohort_lifetime'] = visits['activity_month'] - visits['first_activity_month']

#преобразуем данные в число месяцев, прошедших между датами, и коруглим и приведем эти данные к типу int
visits['cohort_lifetime'] = visits['cohort_lifetime'] / np.timedelta64(1, 'M')
visits['cohort_lifetime'] = visits['cohort_lifetime'].astype('int')


# In[28]:


#сгруппируем данные по когорному столбцу first_activity_month и по столбцу жизненного цикла когорты
cohorts = visits.groupby(['first_activity_month','cohort_lifetime']).agg({'uid':'nunique'}).reset_index() 


# In[29]:


#найдем исходное количество пользователей в первый месяц жизни когорты
initial_users_count = cohorts[cohorts['cohort_lifetime'] == 0][['first_activity_month', 'uid']]
print(initial_users_count) 


# In[30]:


#переименуем столбец uid в получившейся таблице, чтобы потом объединить ее с основной cohorts
initial_users_count = initial_users_count.rename(columns={'uid':'cohort_users'})


# In[31]:


#объединим таблицы в одну общую
cohorts = cohorts.merge(initial_users_count,on='first_activity_month') 


# In[32]:


#найдем Retention Rate
cohorts['retention'] = cohorts['uid'] / cohorts['cohort_users']


# In[33]:


cohorts.head(10)


# In[34]:


#уберем из таблица когорт нулевую(первую) когорту для наглядности изображения тепловой карты
cohorts = cohorts.loc[cohorts['cohort_lifetime'] != 0]


# In[35]:


retention_mean = cohorts[cohorts['cohort_lifetime'] == 1]['retention'].mean()
print("Среднее значение Retention Rate на второй месяц жизни когорты: {:.3f}".format(retention_mean))


# In[36]:


#построим сводную таблицу по данным Retention Rate
retention_pivot = cohorts.pivot_table(
    index='first_activity_month',
    columns='cohort_lifetime',
    values='retention',
    aggfunc='sum',
) 
print(retention_pivot)


# In[37]:


#сократим количество символов в индексах таблицы, для удобства вывода тепловой карты
retention_pivot.index = [str(x)[0:10] for x in retention_pivot.index]


# In[38]:


#построим тепловую карту Retention Rate
sns.set(style='white')
plt.figure(figsize=(13, 9))
plt.title('Тепловая карта коэффициента удержания пользователей в разрезе когорт по данным Яндекс.Афиши с июня 2017 по май 2018')
sns.heatmap(retention_pivot, annot=True, fmt='.1%', linewidths=1, linecolor='gray')
plt.xlabel('Жизненный цикл когорт, месяцев')
plt.ylabel('Месяц первой активности посетителей сайта')
plt.show()


# #### Выводы

# - Среднее значение Retention Rate на второй месяц жизни когорты: 0.065 или 6,5%.
# 
# Анализ показателя удержания клиентов дает нам следующую информацию:
# 
# - с июня по ноябрь 2017 года сравнительно высокий показатель Retention Rate в начальных месяцах жизни когорт (почти 8%)
# 
# - самый высокий показатель Retention Rate во втором месяце жизни "сентябрьской" когорты - 8,5%, также показатели по сентябрю в других когортах выше, чем в других месяцах: необходимо проанализировать источники привлечения этого месяца, возможно будет найден эффективный источник привлечения нвоых клиентов и возврата старых. В том числе, сентябрьское повышение интереса к сайту можно объяснить тем, что пользователи возвращаются с летних каникул, отпусков, планируют походы в кино/театры/концерты, так как это еще и начало сезона во всех подобных заведениях
# 
# - в "июльской" когорте есть гэп во втором месяце жизни когорты, где показатель удержания сильно ниже соседних когорт в этом же месяце, также есть гэп в третьем месяце жизни июньской когорты (для нее это тоже месяц июль): необходимо проанализировать маркетинговые источники, кампании в июле 2017 года, потому что скорее всего там использовали неэффективный инструмент, который не стоит больше применять
# 
# - присутствуют единичные "всплески" активности например в шестой месяц жизни июньской когорты, в первый месяц жизни сентябрьской когорты. Возможно в эти периоды были наиболее удачные рекламные кампании
# 

# ## Метрики электронной коммерции

# ### Анализ времени, необходимого для совершения первой покупки после первого посещения сайта пользователями

# In[39]:


#добавим день и месяц заказа в таблицы
orders['order_dt'] = orders['order_date'].dt.date
orders['order_month'] = orders['order_date'].astype('datetime64[M]')

#найдем время покупки для каждого покупателя
first_order = orders.groupby('uid').agg({'order_date':'min'}).reset_index()
first_order.columns = ['uid', 'first_order_date']
first_order['first_order_dt'] = first_order['first_order_date'].dt.date
first_order['first_order_month'] = first_order['first_order_date'].astype('datetime64[M]')
first_order.head()


# In[40]:


#объединим данные о первых покупках с данными о первом посещении на сайт
buyers = pd.merge(first_activity_date, first_order, on='uid')
buyers.head()


# In[41]:


#переведем в формат времени и даты столбцы в новой таблице
buyers['first_order_dt'] = pd.to_datetime(buyers['first_order_dt'])
buyers['first_activity_date'] = pd.to_datetime(buyers['first_activity_date'])


# In[42]:


#найдем, сколько дней требуется для каждого покупателя, чтобы совершить первую покупку
buyers['days_to_first_order'] = ((buyers['first_order_date'] - buyers['first_activity_date']) / np.timedelta64(1,'D')).astype('int')
buyers.head()


# In[43]:


(
    buyers['days_to_first_order'].plot(kind='hist', bins=50, figsize=(12,7))
    .set(title='Распределение времени от первого посещения сайта пользователями до первой покупки',
        xlabel='Дней после первого посещения сайта',
        ylabel='Частота')
)
plt.xlim(0,75)
plt.show()


# In[44]:


#найдем среднее время, необходимое для совершения первой покупки после первого посещения сайта пользователями
mean = buyers['days_to_first_order'].mean()
print("Среднее время для совершения первой покупки после первого посещения сайта пользователями: {:.1f} дней.".format(mean))


# #### Вывод

# Среднее время для совершения первой покупки после первого посещения сайта пользователями: 16.7 дней.
# По графику распределения времени от первого посещения сайта пользователями до первой покупки можно сделать вывод, что большинство посетителей совершают первую покупку на сайте меньше, чем через 10 дней после первого визита. Однако есть часть покупателей, которым требуется больше времени для принятия решения о покупке. Возможно, стоит взять в работу именно эту часть покупателей, чтобы сократить их время совершения первой покупки.

# ### Анализ среднего количества покупок на одного покупателя за 6 месяцев

# In[45]:


#выделим срез по данным о покупках за полгода с начала исследования
orders_filtered = orders.query('order_date < "2017-12-01 00:00:00"')
orders_filtered.head()


# In[46]:


#сгруппируем данные за полгода
orders_mean = orders_filtered.groupby('uid')['order_date'].count().mean()


# In[47]:


#найдем среднее по количеству покупок на одного пользователя 
print("Среднее количество покупок на одного пользователя в течение июня-ноября 2017 года: {:.1f}".format(orders_mean))


# ### Анализ среднего чека в разрезе времени совершения покупки

# In[48]:


avg_order = orders.groupby('order_date')['revenue'].sum().mean()
max_order = orders.groupby('order_date')['revenue'].sum().max()
min_order = orders.groupby('order_date')['revenue'].sum().min()
print("Средний чек одной покупки на сайте: {:.2f} у.е.".format(avg_order))
print("Максимальный чек одной покупки на сайте: {:.2f} у.е.".format(max_order))
print("Минимальный чек одной покупки на сайте: {:.2f} у.е.".format(min_order))


# In[49]:


orders['order_date_filtered'] = orders['order_date'].dt.date 
order_grouped = orders.groupby('order_date_filtered').agg({'revenue':'sum'}).reset_index()
print(order_grouped)


# In[50]:


plt.figure(figsize = (16,10), dpi = 80)
plt.plot('order_date_filtered', 'revenue', data = order_grouped, color = 'tab:brown')
plt.title("Изменение среднего чека покупок на сайте Яндекс.Афиши с июня 2017 по конец мая 2018 года", fontsize=22)
plt.grid(axis = 'both', alpha = 0.3)
plt.ylabel('Сумма чека, у.е.')
plt.show()


# #### Вывод

# - Средний чек одной покупки на сайте: 5.48 у.е.
# - Максимальный чек одной покупки на сайте: 2633.28 у.е.
# - Минимальный чек одной покупки на сайте: 0.00 у.е.
# 
# Анализ изменения во времени среднего чека одной покупки дает следующую информацию:
# - были сильные скачки покупок в декабре 2017 и июне 2018 года: период предновогодних каникул/отпусков и летних каникул/отпусков
# - самый "неприбыльный" период - август 2017 года
# - период наиболее активных продаж - октбярь, декабрь 2017 и февраль, март 2018 года. Это совпадает в том числе со школьными каникулами.
# 
# Рекламные кампании можно планировать (или увеличивать), подстариваясь под периоды с наибольшим чеком покупок.

# ### Изменение показателя LTV в разрезе когорт

# In[51]:


#выделим месяцы из дат в таблицах с заказами и расходами
orders['order_month'] = orders['order_date'].astype('datetime64[M]')
costs['cost_month'] = costs['cost_date'].astype('datetime64[M]') 


# In[52]:


#найдем месяц первой покупки для каждого посетителя сайта
first_orders = orders.groupby('uid').agg({'order_month': 'min'}).reset_index()

#заменим имя столбца
first_orders.columns = ['uid', 'first_order_month']
print(first_orders.head()) 


# In[53]:


#посчитаем количество новых покупателей (new_buyers) за каждый месяц
cohort_sizes = (first_orders.groupby('first_order_month').agg({'uid': 'nunique'}).reset_index())

#присвоим новые названия столбцам
cohort_sizes.columns = ['first_order_month', 'new_buyers']
print(cohort_sizes.head()) 


# In[54]:


#построим когорты добавив месяц первой покупки каждого покупателя в таблицу с заказами
orders_new = pd.merge(orders,first_orders, on='uid')
print(orders_new.head()) 


# In[55]:


#сгруппируем таблицу заказов по месяцу первой покупки и месяцу каждого заказа и сложим выручку
cohorts_1 = (orders_new.groupby(['first_order_month', 'order_month']).agg({'revenue': 'sum'}).reset_index())
print(cohorts_1.head()) 


# In[56]:


#добавим в таблицу cohorts_1 данные о том, сколько людей первый раз совершили покупку в каждый месяц
report = pd.merge(cohort_sizes, cohorts_1, on='first_order_month')
report = report.query('first_order_month < "2017-12-01" & order_month < "2017-12-01"')
print(report.head())


# In[57]:


#найдем валовую прибыль
margin_rate = 1
report['gp'] = report['revenue'] * margin_rate

#выделим возраст когорты в отдельный столбец
report['age'] = (report['order_month'] - report['first_order_month']) / np.timedelta64(1, 'M')
report['age'] = report['age'].round().astype('int')
print(report.head()) 


# In[58]:


#сделаем расчет LTV
report['ltv'] = report['gp'] / report['new_buyers']

#построим сводную таблицу 
output = report.pivot_table(index='first_order_month', columns='age', values='ltv', aggfunc='mean').round()
output.fillna('')


# In[59]:


#посчитаем итоговый LTV первой когорты
ltv_201706 = output.loc['2017-06-01'].sum()
print(ltv_201706)


# In[60]:


report_grouped = report.groupby('first_order_month')['ltv'].sum()
report_grouped.plot()
plt.title("Изменение показателя LTV на сайте Яндекс.Афиши с июня по ноябрь 2017 года", fontsize=13)
plt.grid(axis = 'both', alpha = 0.3)
plt.xlabel('Месяц первого заказа')
plt.ylabel('LTV')
plt.show()


# #### Вывод

# Был взят временной промежук в шесть месяцев для изучения показателя изменения пожизненной ценности покупателя LTV в разрезе когорт. В среднем каждый покупатель из первой когорты принес по 8 у.е. валовой прибыли за 6 месяцев «жизни».
# К концу изучаемого отрезка времени LTV стремится к нулю, но есть скачок в сентябре. Эта таблица позволяет выделить наиболее лояльную когорту покупателей, с которыми возможно еще более глубокое взаимодействие. 

# ## Маркетинговые метрики

# ### Анализ расходов на маркетинг по источникам

# In[61]:


#найдем общую сумму расходов на маркетинг за исследубемый период
print("Затраты на маркетинг за период с 06.2017 по 05.2018: {:.0f} у.е.".format(costs['costs'].sum()))


# In[62]:


#проиллюстрируем на графике, как менялись затраты на маркетинг во времени
plt.figure(figsize = (16,10), dpi = 50)
plt.bar('cost_date', 'costs', data = costs, color = 'tab:green')
plt.title("Изменение затрат на маркетинг по сайту Яндекс.Афиши с июня 2017 года по май 2018 года", fontsize=18)
plt.grid(axis = 'both', alpha = 0.7)
plt.ylabel('Затраты на маркетинг, у.е.')
plt.show()


# In[63]:


#исследуем как расходы на маркетинг распределены по источникам
costs_per_source = costs.groupby('source_id')['costs'].sum()
print(costs_per_source)


# In[64]:


#проиллюстрируем на графике, как распределены расходы по источникам
(
    costs
    .pivot_table(index='source_id', values='costs').sort_values('costs', ascending = False)
    .plot(y='costs', kind='barh', figsize=(20, 8), title='Распределение маркетинговых расходов по источникам', grid=True, color='green', legend=False, )
    .set(xlabel='Сумма затрат на источник, у.е.', ylabel='Источник продвижения сайта')
)
plt.show()


# #### Вывод

# - Затраты на маркетинг за период с 06.2017 по 05.2018гг составили 329132 у.е.
# - В целом распределение затрат на маркетинг по времени равномерно, но есть отдельные периоды, где затраты повышаются - с октября 2017 по март 2018 и единично в мае-июне 2018. Скорее всего, наиболее эффективным будет синхронизировать время наибольшей активности пользователей с затратами на рекламу. Запускать ее активно до этого перида и в течение его. Например, в нашем случае, это могло быть так: наибольшие затраты на рекламные источники в конце ноября и весь декабрь 2017г, в середине мая и до середины июня 2018г, далее равномерно распределить часть бюджета с середины сентбяря по середину ноября 2017г, в марте 2018г. Оставшийся бюджет распределить по остальным месяцам, возможно оставив август 2017г без большей части рекламы.
# - Анализ распределения затрат по источникам показал, что с большим отрывом перевешивает по затратам Источник №3. Он более чем в два раза требовал вложений, чем следующий за ним по уровню затрат Источник №4. Самыми мало-используемыми (или дешевыми) источниками были Источник №10 и Источник №9. Возможно имеет смысл убрать затраты на эти источники и направить освободившиеся средства на более популярные источники, чтобы привлечь еще больше пользователей через них.

# ### Анализ показателя CAC в разрезе одного покупателя для всего проекта и для каждого источника трафика

# In[65]:


#найдем первый источник перехода для каждого пользователя
first_source = visits.sort_values('visit_start').groupby('uid').first() 
first_source = first_source[['source_id']]

#объединим таблицы первого источника и покупателей
buyers = pd.merge(buyers, first_source, left_on='uid', right_index=True)
buyers.head()


# In[66]:


#найдем уникальных покупателей в каждый день
buyers_daily = buyers.groupby(['source_id', 'first_order_dt']).agg({'uid':'count'}).reset_index()

#переименуем колонку новых значений
buyers_daily.rename(columns={'uid':'n_buyers'}, inplace=True)
buyers_daily.head()


# In[67]:


#выделим месяц затрат в отдельный столбец
costs['cost_month'] = costs['cost_date'].astype('datetime64[M]')


# In[68]:


#объединим таблицы затрат и данные по уникальным покупателям в каждый день
costs_new = pd.merge(buyers_daily, costs, left_on=['source_id', 'first_order_dt'], right_on=['source_id','cost_date'])

#найдем показатель САС для каждого покупателя
costs_new['costs_per_buyer'] = costs_new['costs'] / costs_new['n_buyers']
costs_new.head()


# In[69]:


#найдем среднее значение САС на одного покупателя
cac_mean_buyer = costs_new['costs_per_buyer'].mean()
print("Средний САС на одного покупателя: {:.0f}".format(cac_mean_buyer))


# In[70]:


#найдем среднее значение САС для каждого маркетингового источника
cac_mean = costs_new.groupby('source_id')['costs_per_buyer'].mean()
print("Среднее значение показателя САС для каждого маркетингового источника: ", cac_mean)


# In[71]:


#построим график САС в разрезе источников
cac_mean.plot.bar(x='costs_per_buyer', y='source_id', title='Стоимость привлечения клиента по источникам')
plt.show()


# #### Вывод

# Самыми дорогими источниками по стоимости привлечения одного пользователя являются Источник №3(15,5 у.е.) и Источник №2(16,3 у.е.). Другие источники находятся примерно на одном уровне.

# ### Анализ возрата маркетинговых затрат (ROMI) по когортам в разрезе источников

# In[72]:


#найдем первый источник по которому пришел каждый посетитель
first_source = visits.groupby('uid')['source_id'].first().reset_index()
first_source.columns = ['uid', 'source_id']


# In[73]:


#посчитаем количество посетителей, пришедших с каждого источника
cohort_fs = (
    first_source.groupby('source_id')
    .agg({'uid': 'nunique'})
    .reset_index()
)
cohort_fs.columns = ['source_id', 'n_visits']
cohort_fs.head()


# In[74]:


#объединим таблицу first_source с таблицей заказов
visits_first_source = pd.merge(orders, first_source, on='uid')
visits_first_source.head()


# In[75]:


#посчитаем доход в месяц от каждого источника
cohorts = (
    visits_first_source.groupby(['source_id', 'order_month'])
    .agg({'revenue': 'sum'})
    .reset_index()
)
cohorts.head()


# In[76]:


#объединим таблицы
report_fs = pd.merge(cohort_fs, cohorts, on='source_id')
report_fs.head()


# In[77]:


#посчитаем LTV посетителей в разрезе источников
report_fs['ltv'] = report_fs['revenue'] / report_fs['n_visits']
report_fs.head()


# In[78]:


#объединим таблицы
merged = pd.merge(report_fs, costs, on='source_id', how='left')
merged.head()


# In[79]:


#найдем расходы на привлечение каждого посетителя сайта по источникам
merged['cac_per_source_new'] = merged['costs'] / merged['n_visits']
merged.head()


# In[80]:


#ROMI
merged['romi'] = merged['ltv'] / merged['cac_per_source_new']
merged.head()


# In[81]:


#сумма ROMI по источникам
romi = merged.groupby('source_id')['romi'].mean().round()
romi.head(10)


# In[82]:


#отобразим на графике распределение ROMI по источникам
(
    merged
    .pivot_table(index='source_id', values='romi').sort_values('romi', ascending = False)
    .plot(y='romi', kind='barh', figsize=(20, 8), title='Распределение возврата затрат на посетителя сайта по источникам', grid=True, color='green', legend=False, )
    .set(xlabel='Возврат на привлечение посетителя сайта, у.е.', ylabel='Источник продвижения сайта')
)
plt.show()


# In[83]:


#построим график распределения romi по источникам во времени
def analysis(df, data):    
    fig = px.line(df.pivot_table(index = ['source_id', 'cost_month'], values = data, aggfunc = 'sum').reset_index(), x = 'cost_month', y = data, color = 'source_id', title = 'Распределение ROMI по источникам во времени')
    fig.show()
    
analysis(merged, 'romi')


# #### Вывод

# - самый окупаемый источник - Источник №4 (в среднем 108 у.е. с человека)
# - наименее окупаемый источник - Источник №3 (в среднем 13 у.е. с человека)
# 
# Анализ источников и их окупаемости:
# - Источник №4 имеет четкие границы, когда он сверхокупаемый, но так же есть и мериоды, где отдача от него такая же, как у других источников. Возможно, нужно основываться на этой информации при распределении маркетингового бюджета, выбирая наиболее окупаемые периоды. Таковыми для Источника №4 являются: август 2017, октябрь 2017, март 2018, май 2018.
# - Источник №5 показал свою сверхокупаемость исключительно в марте 2018 года, в остальные периоды ROMI низкий.
# - Источник №1 наиболее окупаем только в июле и в августе 2017 года.
# - Источники №2, №9 и №10 имею примерно одинаковую кривую на графике, ROMI невысокий, но за период август 2017 года есть повышение этого показателя
# - Источник №3 имеет наихудший ROMI, предполагаю, что от него лучше отказаться, перераспределив освободившиеся средства на другие более выгодные источники

# ##  Выводы и рекомендации

# 3.1. Определите источники трафика, на которые маркетологам стоит делать упор. Объясните свой выбор: на какие метрики вы ориентируетесь и почему;
# 3.2. Опишите выводы, которые вы сделали после подсчёта метрик каждого вида: маркетинговых, продуктовых и метрик электронной коммерции;
# 3.3. Подведите итоги когортного анализа. Определите самые перспективные для компании когорты клиентов;

# 1. Основные цифры анализа
# 
# 1.1 
# Количество уникальных посетителей в день в среднем: 907
# Количество уникальных посетителей в неделю в среднем: 5716
# Количество уникальных посетителей в месяц в среднем: 23228
# 
# График уникальных дневных посещений позволяет сделать вывод, что посещения сайта равномерны до середины месяца, а ближе к концу (25-30 числа) бывают всплески с максимальными посещениями. Скорее всего, это совпадает с датой вылаты заработной платы у посетителей. Когда у них появляются средства, они готовы бывают их потратить. Возможно, следует увеличивать количество рекламы в интернете именно в эти даты, чтобы привлекать больше посетителей и покупателей.
# 
# 1.2
# Годовой график уникальных посещений показал, что летом присходит спад активности посетителей сайта, но с октября по март активность почти в два раза выше весенне-летней. Скорее всего это связано с тем, что в осенне-зимний период люди меньше путешествуют, нет дачных забот, и нет желания проводить время на улице из-за плохой погоды, поэтому возрастает интерес к концертно-театральным развлечениям. Плюс это праздничные дни, дни школьных каникул, когда много людей выбираются в праздничные новогодние дни отдохнуть.
# 
# Количество посещений сайта в день в среднем: 987
# Количество сессий одного посетителя в день в среднем: 1.58
# Среднедневное посещение сайта в день всеми пользователями всего на 10% больше, чем показатель среднедневного посещения уникальными пользователями. Можно предположить, что доля посетителей, возвращающихся на сайт, низка. Об этом же может говорить показатель среднего числа сессий одного посетителя в день. И вновь, у данных есть цикличность - наибольшие всплески посещений сайта наблюдаются в конце месяца 25-30 числах.
# 
# 1.3
# За средний показатель продолжительности посещения сайта мы возьмем медиану: 300 секунд.
# На графике продолжительности посещения сайта есть выброс. Возможно, сайт плохо отображается в мобильной версии — и все сессии со смартфонов и планшетов очень короткие. Возможно, ссылки с переходов работают с ошибкой - и переход происходит, но тут же обрывается.
# 
# 1.4
# Анализ показателя удержания клиентов дает нам следующую информацию:
# - с июня по ноябрь 2017 года сравнительно высокий показатель Retention Rate в начальных месяцах жизни когорт (почти 8%)
# - самый высокий показатель Retention Rate во втором месяце жизни "сентябрьской" когорты - 8,5%, также показатели по сентябрю в других когортах выше, чем в других месяцах: необходимо проанализировать источники привлечения этого месяца, возможно будет найден эффективный источник привлечения новых клиентов и возврата старых. В том числе, сентябрьское повышение интереса к сайту можно объяснить тем, что пользователи возвращаются с летних каникул, отпусков, планируют походы в кино/театры/концерты, так как это еще и начало сезона во всех подобных заведениях
# - в "июльской" когорте есть гэп во втором месяце жизни когорты, где показатель удержания сильно ниже соседних когорт в этом же месяце, также есть гэп в третьем месяце жизни июньской когорты (для нее это тоже месяц июль)
# 
# 1.5
# Среднее время для совершения первой покупки после первого посещения сайта пользователями: 16.7 дней. По графику распределения времени от первого посещения сайта пользователями до первой покупки можно сделать вывод, что большинство посетителей совершают первую покупку на сайте меньше, чем через 10 дней после первого визита. Однако есть часть покупателей, которым требуется больше времени для принятия решения о покупке. Возможно, стоит взять в работу именно эту часть покупателей, чтобы сократить их время совершения первой покупки.
# 
# 1.6
# Среднее количество покупок на одного пользователя в течение июня-ноября 2017 года: 1.3
# Средний чек одной покупки на сайте: 5.48 у.е.
# Анализ изменения во времени среднего чека одной покупки дает следующую информацию:
# - были сильные скачки покупок в декабре 2017 и июне 2018 года: период предновогодних каникул/отпусков и летних каникул/отпусков
# - самый "неприбыльный" период - август 2017 года
# - период наиболее активных продаж - октбярь, декабрь 2017 и февраль, март 2018 года. Это совпадает в том числе со школьными каникулами.
# Рекламные кампании можно планировать (или увеличивать), подстариваясь под периоды с наибольшим чеком покупок.
# 
# 1.7
# Был взят временной промежук в шесть месяцев для изучения показателя изменения пожизненной ценности покупателя LTV в разрезе когорт. В среднем каждый покупатель из первой когорты принес по 8 у.е. валовой прибыли за 6 месяцев «жизни». К концу изучаемого отрезка времени LTV стремится к нулю, но есть скачок в сентябре. 
# 
# 1.8
# Затраты на маркетинг за период с 06.2017 по 05.2018гг составили 329132 у.е.
# В целом распределение затрат на маркетинг по времени равномерно, но есть отдельные периоды, где затраты повышаются - с октября 2017 по март 2018 и единично в мае-июне 2018. Скорее всего, наиболее эффективным будет синхронизировать время наибольшей активности пользователей с затратами на рекламу. Запускать ее активно до этого перида и в течение него. Например, в нашем случае, это могло быть так: наибольшие затраты на рекламные источники в конце ноября и весь декабрь 2017г, в середине мая и до середины июня 2018г, далее равномерно распределить часть бюджета с середины сентбяря по середину ноября 2017г, в марте 2018г. Оставшийся бюджет распределить по остальным месяцам, возможно оставив август 2017г без большей части рекламы.
# Анализ распределения затрат по источникам показал, что с большим отрывом перевешивает по затратам Источник №3. Он более чем в два раза требовал вложений, чем следующий за ним по уровню затрат Источник №4. Самыми мало-используемыми (или дешевыми) источниками были Источник №10 и Источник №9. Возможно имеет смысл убрать затраты на эти источники и направить освободившиеся средства на более популярные источники, чтобы привлечь еще больше пользователей через них.
# 
# 1.9
# Самыми дорогими источниками по стоимости привлечения одного пользователя являются Источник №3(15,5 у.е.) и Источник №2(16,3 у.е.). Другие источники находятся примерно на одном уровне.
# 
# 1.10
# -самый окупаемый источник - Источник №4 (в среднем 108 у.е. с человека)
# - наименее окупаемый источник - Источник №3 (в среднем 13 у.е. с человека)
# Анализ источников и их окупаемости:
# -Источник №4 имеет четкие границы, когда он сверхокупаемый, но так же есть и мериоды, где отдача от него такая же, как у других источников. Возможно, нужно основываться на этой информации при распределении маркетингового бюджета, выбирая наиболее окупаемые периоды. Таковыми для Источника №4 являются: август 2017, октябрь 2017, март 2018, май 2018.
# -Источник №5 показал свою сверхокупаемость исключительно в марте 2018 года, в остальные периоды ROMI низкий.
# -Источник №1 наиболее окупаем только в июле и в августе 2017 года.
# -Источники №2, №9 и №10 имею примерно одинаковую кривую на графике, ROMI невысокий, но за период август 2017 года есть повышение этого показателя
# -Источник №3 имеет наихудший ROMI, предполагаю, что от него лучше отказаться
# 
# 
# 2. Наиболее перспективный источник трафика
# 
# Наиболее перспективным источником трафика следует считать Источник №4, так как при стоимости привлечения одной из самых низких, он принес наибольшую окупаемость с клиента. Но затраты на него следует распределить по периодам. Предполагаю, что нужно исключить или уменьшить затраты на Источник №3, так как он, являясь самым дорогим, принес наименьшую прибыль с покупателя. По остальным источникам необходимо так же ориентироваться на периоды их окупаемости и усиливать затраты на них в эти месяцы.
# 
# 
# 3. Наиболее перспективная когорта клиентов
# Скорее всего все когорты имеют дальнейший потенциал к увеличению и развитию, и после применения рекомендаций выше показатель удержания  Retention Rate увеличится. Однако, предположу, что перспективными когортами могут быть те, которые во второй месяц их жизни показывали чуть более позитивные результаты: это когорты июня, августа и сентября.
