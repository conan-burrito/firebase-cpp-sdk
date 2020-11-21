#include <firebase/app.h>

int main() {
   ::firebase::AppOptions default_options{};
   default_options.set_app_id("dummy-app-id");
   default_options.set_api_key("dummy-api-key");
   default_options.set_project_id("dummy-project-id");
   ::firebase::App *app;
#if defined(__ANDROID__)
   app = ::firebase::App::Create(default_options, nullptr, nullptr);
#else
   app = ::firebase::App::Create(default_options);
#endif
   delete app;

   return 0;
}
