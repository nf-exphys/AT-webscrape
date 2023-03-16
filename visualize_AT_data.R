library(tidyverse)

files <- list.files("./data/", full.names = T)

data <- map(files, read_csv, show_col_types = FALSE) %>% 
  bind_rows(.) %>% 
  janitor::clean_names() %>% 
  filter(year != 2021) %>% 
  mutate(state = as.factor(state),
         direction = tolower(direction),
         direction = as.factor(direction),
         year = as.factor(year))

ggplot(data, aes(x = year, fill = direction)) +
  geom_bar() + 
  ggtitle("AT Hiking Direction by Year")
  
  
data %>% 
  filter(state == "DC" | state == "VA" | state == "MD") %>% 
  group_by(year, state) %>% 
  summarise(count = n()) %>% 
  mutate(year = as.character(year),
         year = as.numeric(year)) %>% 
  ungroup() %>% 
  ggplot(data = ., aes(x = year, y = count, fill = state)) +
  geom_bar(stat = "identity") + 
  ggtitle("AT Completion in the DMV Area by State") + 
  ylab("Count") +
  xlab("Year") + 
  scale_x_continuous(breaks = seq(2010, 2019, 1))
  
#2018: 1752 for Jan-March, 779 for Apr - June, July - Dec. 21 
attempt_2018 = 1752+779+21
#2019: 1578 for Jan-March, 748 for Apr - June, July - Dec. 21
attempt_2019 = 1578+748+21

data %>% 
  group_by(name) %>% 
  summarise(completions = n()) %>% 
  group_by(completions) %>% 
  summarise(num = n())
